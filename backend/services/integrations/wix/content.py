import re
import uuid
from typing import Any, Dict, List


def parse_markdown_inline(text: str) -> List[Dict[str, Any]]:
    """
    Parse inline markdown formatting (bold, italic, links) into Ricos text nodes.
    Returns a list of text nodes with decorations.
    Handles: **bold**, *italic*, [links](url), `code`, and combinations.
    """
    if not text:
        return [{
            'id': str(uuid.uuid4()),
            'type': 'TEXT',
            'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
            'textData': {'text': '', 'decorations': []}
        }]
    
    nodes = []
    
    # Process text character by character to handle nested/adjacent formatting
    # This is more robust than regex for complex cases
    i = 0
    current_text = ''
    current_decorations = []
    
    while i < len(text):
        # Check for bold **text** (must come before single * check)
        if i < len(text) - 1 and text[i:i+2] == '**':
            # Save any accumulated text
            if current_text:
                nodes.append({
                    'id': str(uuid.uuid4()),
                    'type': 'TEXT',
                    'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
                    'textData': {
                        'text': current_text,
                        'decorations': current_decorations.copy()
                    }
                })
                current_text = ''
            
            # Find closing **
            end_bold = text.find('**', i + 2)
            if end_bold != -1:
                bold_text = text[i + 2:end_bold]
                # Recursively parse the bold text for nested formatting
                bold_nodes = parse_markdown_inline(bold_text)
                # Add BOLD decoration to all text nodes within
                # Per Wix API: decorations are objects with 'type' field, not strings
                for node in bold_nodes:
                    if node['type'] == 'TEXT':
                        node_decorations = node['textData'].get('decorations', []).copy()
                        # Check if BOLD decoration already exists
                        has_bold = any(d.get('type') == 'BOLD' for d in node_decorations if isinstance(d, dict))
                        if not has_bold:
                            node_decorations.append({'type': 'BOLD'})
                        node['textData']['decorations'] = node_decorations
                    nodes.append(node)
                i = end_bold + 2
                continue
        
        # Check for link [text](url)
        elif text[i] == '[':
            # Save any accumulated text
            if current_text:
                nodes.append({
                    'id': str(uuid.uuid4()),
                    'type': 'TEXT',
                    'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
                    'textData': {
                        'text': current_text,
                        'decorations': current_decorations.copy()
                    }
                })
                current_text = ''
                current_decorations = []
            
            # Find matching ]
            link_end = text.find(']', i)
            if link_end != -1 and link_end < len(text) - 1 and text[link_end + 1] == '(':
                link_text = text[i + 1:link_end]
                url_start = link_end + 2
                url_end = text.find(')', url_start)
                if url_end != -1:
                    url = text[url_start:url_end]
                    # Per Wix API: Links are decorations on TEXT nodes, not separate node types
                    # Create TEXT node with LINK decoration
                    nodes.append({
                        'id': str(uuid.uuid4()),
                        'type': 'TEXT',
                        'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
                        'textData': {
                            'text': link_text,
                            'decorations': [{
                                'type': 'LINK',
                                'linkData': {
                                    'link': {
                                        'url': url,
                                        'target': 'BLANK'  # Wix API uses 'BLANK', not '_blank'
                                    }
                                }
                            }]
                        }
                    })
                    i = url_end + 1
                    continue
        
        # Check for code `text`
        elif text[i] == '`':
            # Save any accumulated text
            if current_text:
                nodes.append({
                    'id': str(uuid.uuid4()),
                    'type': 'TEXT',
                    'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
                    'textData': {
                        'text': current_text,
                        'decorations': current_decorations.copy()
                    }
                })
                current_text = ''
                current_decorations = []
            
            # Find closing `
            code_end = text.find('`', i + 1)
            if code_end != -1:
                code_text = text[i + 1:code_end]
                # Per Wix API: CODE is not a valid decoration type, but we'll keep the structure
                # Note: Wix uses CODE_BLOCK nodes for code, not CODE decorations
                # For inline code, we'll just use plain text for now
                nodes.append({
                    'id': str(uuid.uuid4()),
                    'type': 'TEXT',
                    'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
                    'textData': {
                        'text': code_text,
                        'decorations': []  # CODE is not a valid decoration in Wix API
                    }
                })
                i = code_end + 1
                continue
        
        # Check for italic *text* (only if not part of **)
        elif text[i] == '*' and (i == 0 or text[i-1] != '*') and (i == len(text) - 1 or text[i+1] != '*'):
            # Save any accumulated text
            if current_text:
                nodes.append({
                    'id': str(uuid.uuid4()),
                    'type': 'TEXT',
                    'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
                    'textData': {
                        'text': current_text,
                        'decorations': current_decorations.copy()
                    }
                })
                current_text = ''
                current_decorations = []
            
            # Find closing * (but not **)
            italic_end = text.find('*', i + 1)
            if italic_end != -1:
                # Make sure it's not part of **
                if italic_end == len(text) - 1 or text[italic_end + 1] != '*':
                    italic_text = text[i + 1:italic_end]
                    italic_nodes = parse_markdown_inline(italic_text)
                    # Add ITALIC decoration
                    # Per Wix API: decorations are objects with 'type' field
                    for node in italic_nodes:
                        if node['type'] == 'TEXT':
                            node_decorations = node['textData'].get('decorations', []).copy()
                            # Check if ITALIC decoration already exists
                            has_italic = any(d.get('type') == 'ITALIC' for d in node_decorations if isinstance(d, dict))
                            if not has_italic:
                                node_decorations.append({'type': 'ITALIC'})
                            node['textData']['decorations'] = node_decorations
                        nodes.append(node)
                    i = italic_end + 1
                    continue
        
        # Regular character
        current_text += text[i]
        i += 1
    
    # Add any remaining text
    if current_text:
        nodes.append({
            'id': str(uuid.uuid4()),
            'type': 'TEXT',
            'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
            'textData': {
                'text': current_text,
                'decorations': current_decorations.copy()
            }
        })
    
    # If no nodes created, return single plain text node
    if not nodes:
        nodes.append({
            'id': str(uuid.uuid4()),
            'type': 'TEXT',
            'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
            'textData': {
                'text': text,
                'decorations': []
            }
        })
    
    return nodes


def convert_content_to_ricos(content: str, images: List[str] = None) -> Dict[str, Any]:
    """
    Convert markdown content into valid Ricos JSON format.
    Supports headings, paragraphs, lists, bold, italic, links, and images.
    """
    if not content:
        content = "This is a post from ALwrity."
    
    nodes = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        node_id = str(uuid.uuid4())
        
        # Check for headings
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            heading_text = line.lstrip('# ').strip()
            text_nodes = parse_markdown_inline(heading_text)
            nodes.append({
                'id': node_id,
                'type': 'HEADING',
                'nodes': text_nodes,
                'headingData': {'level': min(level, 6)}
            })
            i += 1
        
        # Check for blockquotes
        elif line.startswith('>'):
            quote_text = line.lstrip('> ').strip()
            # Continue reading consecutive blockquote lines
            quote_lines = [quote_text]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(lines[i].strip().lstrip('> ').strip())
                i += 1
            quote_content = ' '.join(quote_lines)
            text_nodes = parse_markdown_inline(quote_content)
            # CRITICAL: TEXT nodes must be wrapped in PARAGRAPH nodes within BLOCKQUOTE
            paragraph_node = {
                'id': str(uuid.uuid4()),
                'type': 'PARAGRAPH',
                'nodes': text_nodes,
                'paragraphData': {}
            }
            blockquote_node = {
                'id': node_id,
                'type': 'BLOCKQUOTE',
                'nodes': [paragraph_node],
                'blockquoteData': {}
            }
            nodes.append(blockquote_node)
        
        # Check for unordered lists (handle both '- ' and '* ' markers)
        elif (line.startswith('- ') or line.startswith('* ') or 
             (line.startswith('-') and len(line) > 1 and line[1] != '-') or
             (line.startswith('*') and len(line) > 1 and line[1] != '*')):
            list_items = []
            list_marker = '- ' if line.startswith('-') else '* '
            # Process list items
            while i < len(lines):
                current_line = lines[i].strip()
                # Check if this is a list item
                is_list_item = (current_line.startswith('- ') or current_line.startswith('* ') or
                               (current_line.startswith('-') and len(current_line) > 1 and current_line[1] != '-') or
                               (current_line.startswith('*') and len(current_line) > 1 and current_line[1] != '*'))
                
                if not is_list_item:
                    break
                
                # Extract item text (handle both '- ' and '-item' formats)
                if current_line.startswith('- ') or current_line.startswith('* '):
                    item_text = current_line[2:].strip()
                elif current_line.startswith('-'):
                    item_text = current_line[1:].strip()
                elif current_line.startswith('*'):
                    item_text = current_line[1:].strip()
                else:
                    item_text = current_line
                
                list_items.append(item_text)
                i += 1
                
                # Check for nested items (indented with 2+ spaces)
                while i < len(lines):
                    next_line = lines[i]
                    # Must be indented and be a list marker
                    if next_line.startswith('  ') and (next_line.strip().startswith('- ') or 
                                                      next_line.strip().startswith('* ') or
                                                      (next_line.strip().startswith('-') and len(next_line.strip()) > 1) or
                                                      (next_line.strip().startswith('*') and len(next_line.strip()) > 1)):
                        nested_text = next_line.strip()
                        if nested_text.startswith('- ') or nested_text.startswith('* '):
                            nested_text = nested_text[2:].strip()
                        elif nested_text.startswith('-'):
                            nested_text = nested_text[1:].strip()
                        elif nested_text.startswith('*'):
                            nested_text = nested_text[1:].strip()
                        list_items.append(nested_text)
                        i += 1
                    else:
                        break
            
            # Build list items with proper formatting
            # CRITICAL: TEXT nodes must be wrapped in PARAGRAPH nodes within LIST_ITEM
            # NOTE: LIST_ITEM nodes do NOT have a data field per Wix API schema
            # Wix API: omit empty data objects, don't include them as {}
            list_node_items = []
            for item_text in list_items:
                item_node_id = str(uuid.uuid4())
                text_nodes = parse_markdown_inline(item_text)
                paragraph_node = {
                    'id': str(uuid.uuid4()),
                    'type': 'PARAGRAPH',
                    'nodes': text_nodes,
                    'paragraphData': {}
                }
                list_item_node = {
                    'id': item_node_id,
                    'type': 'LIST_ITEM',
                    'nodes': [paragraph_node]
                }
                list_node_items.append(list_item_node)
            
            bulleted_list_node = {
                'id': node_id,
                'type': 'BULLETED_LIST',
                'nodes': list_node_items,
                'bulletedListData': {}
            }
            nodes.append(bulleted_list_node)
        
        # Check for ordered lists
        elif re.match(r'^\d+\.\s+', line):
            list_items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                item_text = re.sub(r'^\d+\.\s+', '', lines[i].strip())
                list_items.append(item_text)
                i += 1
                # Check for nested items
                while i < len(lines) and lines[i].strip().startswith('  ') and re.match(r'^\s+\d+\.\s+', lines[i].strip()):
                    nested_text = re.sub(r'^\s+\d+\.\s+', '', lines[i].strip())
                    list_items.append(nested_text)
                    i += 1
            
            # CRITICAL: TEXT nodes must be wrapped in PARAGRAPH nodes within LIST_ITEM
            # NOTE: LIST_ITEM nodes do NOT have a data field per Wix API schema
            # Wix API: omit empty data objects, don't include them as {}
            list_node_items = []
            for item_text in list_items:
                item_node_id = str(uuid.uuid4())
                text_nodes = parse_markdown_inline(item_text)
                paragraph_node = {
                    'id': str(uuid.uuid4()),
                    'type': 'PARAGRAPH',
                    'nodes': text_nodes,
                    'paragraphData': {}
                }
                list_item_node = {
                    'id': item_node_id,
                    'type': 'LIST_ITEM',
                    'nodes': [paragraph_node]
                }
                list_node_items.append(list_item_node)
            
            ordered_list_node = {
                'id': node_id,
                'type': 'ORDERED_LIST',
                'nodes': list_node_items,
                'orderedListData': {}
            }
            nodes.append(ordered_list_node)
        
        # Check for images
        elif line.startswith('!['):
            img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            if img_match:
                alt_text = img_match.group(1)
                img_url = img_match.group(2)
                nodes.append({
                    'id': node_id,
                    'type': 'IMAGE',
                    'nodes': [],
                    'imageData': {
                        'image': {
                            'src': {'url': img_url},
                            'altText': alt_text
                        },
                        'containerData': {
                            'alignment': 'CENTER',
                            'width': {'size': 'CONTENT'}
                        }
                    }
                })
            i += 1
        
        # Regular paragraph
        else:
            # Collect consecutive non-empty lines as paragraph content
            para_lines = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    break
                # Stop if next line is a special markdown element
                if (next_line.startswith('#') or 
                    next_line.startswith('- ') or 
                    next_line.startswith('* ') or
                    next_line.startswith('>') or
                    next_line.startswith('![') or
                    re.match(r'^\d+\.\s+', next_line)):
                    break
                para_lines.append(next_line)
                i += 1
            
            para_text = ' '.join(para_lines)
            text_nodes = parse_markdown_inline(para_text)
            
            # Only add paragraph if there are text nodes
            if text_nodes:
                paragraph_node = {
                    'id': node_id,
                    'type': 'PARAGRAPH',
                    'nodes': text_nodes,
                    'paragraphData': {}
                }
                nodes.append(paragraph_node)
    
    # Ensure at least one node exists
    # Wix API: omit empty data objects, don't include them as {}
    if not nodes:
        fallback_paragraph = {
            'id': str(uuid.uuid4()),
            'type': 'PARAGRAPH',
            'nodes': [{
                'id': str(uuid.uuid4()),
                'type': 'TEXT',
                'nodes': [],  # TEXT nodes must have empty nodes array per Wix API
                'textData': {
                    'text': content[:500] if content else "This is a post from ALwrity.",
                    'decorations': []
                }
            }],
            'paragraphData': {}
        }
        nodes.append(fallback_paragraph)
    
    # Per Wix Blog API documentation: richContent should ONLY contain 'nodes'
    # Do NOT include 'type', 'id', 'metadata', or 'documentStyle' at root level
    # These fields are for Ricos Document format, but Blog API expects just the nodes structure
    return {
        'nodes': nodes
    }


