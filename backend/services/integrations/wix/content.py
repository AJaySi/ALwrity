import re
import uuid
from typing import Any, Dict, List


def parse_markdown_inline(text: str) -> List[Dict[str, Any]]:
    """
    Parse inline markdown formatting (bold, italic, links, code, strikethrough) into Ricos text nodes.
    Returns a list of text nodes with decorations.
    Handles: **bold**, *italic*, [links](url), `code`, ~strikethrough~, and combinations.
    """
    if not text:
        return [{
            'id': str(uuid.uuid4()),
            'type': 'TEXT',
            'nodes': [],
            'textData': {'text': '', 'decorations': []}
        }]
    
    nodes = []
    i = 0
    current_text = ''
    
    def flush_text():
        nonlocal current_text
        if current_text:
            nodes.append({
                'id': str(uuid.uuid4()),
                'type': 'TEXT',
                'nodes': [],
                'textData': {'text': current_text, 'decorations': []}
            })
            current_text = ''
    
    while i < len(text):
        # Bold **text**
        if i < len(text) - 1 and text[i:i+2] == '**':
            flush_text()
            end_bold = text.find('**', i + 2)
            if end_bold != -1:
                bold_text = text[i + 2:end_bold]
                bold_nodes = parse_markdown_inline(bold_text)
                for node in bold_nodes:
                    if node['type'] == 'TEXT':
                        decs = node['textData'].get('decorations', []).copy()
                        if not any(d.get('type') == 'BOLD' for d in decs if isinstance(d, dict)):
                            decs.append({'type': 'BOLD'})
                        node['textData']['decorations'] = decs
                    nodes.append(node)
                i = end_bold + 2
                continue
        
        # Strikethrough ~text~
        elif text[i] == '~':
            flush_text()
            end_strike = text.find('~', i + 1)
            if end_strike != -1:
                strike_text = text[i + 1:end_strike]
                strike_nodes = parse_markdown_inline(strike_text)
                for node in strike_nodes:
                    if node['type'] == 'TEXT':
                        decs = node['textData'].get('decorations', []).copy()
                        if not any(d.get('type') == 'STRIKETHROUGH' for d in decs if isinstance(d, dict)):
                            decs.append({'type': 'STRIKETHROUGH'})
                        node['textData']['decorations'] = decs
                    nodes.append(node)
                i = end_strike + 1
                continue
        
        # Link [text](url)
        elif text[i] == '[':
            flush_text()
            link_end = text.find(']', i)
            if link_end != -1 and link_end < len(text) - 1 and text[link_end + 1] == '(':
                link_text = text[i + 1:link_end]
                url_start = link_end + 2
                url_end = text.find(')', url_start)
                if url_end != -1:
                    url = text[url_start:url_end]
                    nodes.append({
                        'id': str(uuid.uuid4()),
                        'type': 'TEXT',
                        'nodes': [],
                        'textData': {
                            'text': link_text,
                            'decorations': [{
                                'type': 'LINK',
                                'linkData': {
                                    'link': {
                                        'url': url,
                                        'target': 'BLANK'
                                    }
                                }
                            }]
                        }
                    })
                    i = url_end + 1
                    continue
        
        # Inline code `text`
        elif text[i] == '`':
            flush_text()
            code_end = text.find('`', i + 1)
            if code_end != -1:
                code_text = text[i + 1:code_end]
                # Wix doesn't have a CODE decoration, but we can preserve the text
                nodes.append({
                    'id': str(uuid.uuid4()),
                    'type': 'TEXT',
                    'nodes': [],
                    'textData': {
                        'text': code_text,
                        'decorations': []  # CODE is not a valid decoration in Wix API
                    }
                })
                i = code_end + 1
                continue
        
        # Italic *text* (must come after ** check)
        elif text[i] == '*' and (i == 0 or text[i-1] != '*') and (i == len(text) - 1 or text[i+1] != '*'):
            flush_text()
            italic_end = text.find('*', i + 1)
            if italic_end != -1:
                # Make sure it's not part of **
                if italic_end == len(text) - 1 or text[italic_end + 1] != '*':
                    italic_text = text[i + 1:italic_end]
                    italic_nodes = parse_markdown_inline(italic_text)
                    for node in italic_nodes:
                        if node['type'] == 'TEXT':
                            decs = node['textData'].get('decorations', []).copy()
                            if not any(d.get('type') == 'ITALIC' for d in decs if isinstance(d, dict)):
                                decs.append({'type': 'ITALIC'})
                            node['textData']['decorations'] = decs
                        nodes.append(node)
                    i = italic_end + 1
                    continue
        
        # Regular character
        current_text += text[i]
        i += 1
    
    flush_text()
    
    # If no nodes created, return single plain text node
    if not nodes:
        nodes.append({
            'id': str(uuid.uuid4()),
            'type': 'TEXT',
            'nodes': [],
            'textData': {'text': text, 'decorations': []}
        })
    
    return nodes


def _make_code_block_node(code_text: str, language: str = '') -> Dict[str, Any]:
    """Create a Ricos CODE_BLOCK node."""
    lines = code_text.split('\n')
    text_nodes = []
    for line in lines:
        text_nodes.append({
            'id': str(uuid.uuid4()),
            'type': 'TEXT',
            'nodes': [],
            'textData': {'text': line, 'decorations': []}
        })
    
    return {
        'id': str(uuid.uuid4()),
        'type': 'CODE_BLOCK',
        'nodes': text_nodes,
        'codeBlockData': {
            'language': language or 'text',
            'textWrap': True
        }
    }


def _make_horizontal_rule_node() -> Dict[str, Any]:
    """Create a Ricos DIVIDER node."""
    return {
        'id': str(uuid.uuid4()),
        'type': 'DIVIDER',
        'nodes': [],
        'dividerData': {
            'type': 'LINE',
            'lineStyle': {
                'width': 'LARGE',
                'alignment': 'CENTER'
            }
        }
    }


def convert_content_to_ricos(content: str, images: List[str] = None) -> Dict[str, Any]:
    """
    Convert markdown content into valid Ricos JSON format.
    
    Supports:
    - Headings (# to ######)
    - Paragraphs with inline formatting
    - Unordered lists (-, *)
    - Ordered lists (1., 2.)
    - Blockquotes (>)
    - Code blocks (```language ... ```)
    - Inline images (![alt](url))
    - Horizontal rules (---, ***, ___)
    """
    if not content:
        content = "This is a post from ALwrity."
    
    nodes = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not stripped:
            i += 1
            continue
        
        node_id = str(uuid.uuid4())
        
        # Code blocks (```language ... ```)
        if stripped.startswith('```'):
            language = stripped[3:].strip() or ''
            code_lines = []
            i += 1
            while i < len(lines):
                if lines[i].strip() == '```':
                    i += 1
                    break
                code_lines.append(lines[i])
                i += 1
            code_text = '\n'.join(code_lines)
            if code_text.strip():
                nodes.append(_make_code_block_node(code_text, language))
            continue
        
        # Horizontal rules
        if re.match(r'^(---+|\*\*\*|___+)$', stripped):
            nodes.append(_make_horizontal_rule_node())
            i += 1
            continue
        
        # Headings
        if stripped.startswith('#'):
            level = len(stripped) - len(stripped.lstrip('#'))
            heading_text = stripped.lstrip('# ').strip()
            text_nodes = parse_markdown_inline(heading_text)
            nodes.append({
                'id': node_id,
                'type': 'HEADING',
                'nodes': text_nodes,
                'headingData': {'level': min(level, 6)}
            })
            i += 1
            continue
        
        # Blockquotes
        if stripped.startswith('>'):
            quote_lines = [stripped.lstrip('> ').strip()]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(lines[i].strip().lstrip('> ').strip())
                i += 1
            quote_content = ' '.join(quote_lines)
            text_nodes = parse_markdown_inline(quote_content)
            paragraph_node = {
                'id': str(uuid.uuid4()),
                'type': 'PARAGRAPH',
                'nodes': text_nodes,
            }
            nodes.append({
                'id': node_id,
                'type': 'BLOCKQUOTE',
                'nodes': [paragraph_node],
            })
            continue
        
        # Unordered lists
        if (stripped.startswith('- ') or stripped.startswith('* ') or 
            (stripped.startswith('-') and len(stripped) > 1 and stripped[1] != '-') or
            (stripped.startswith('*') and len(stripped) > 1 and stripped[1] != '*')):
            list_items = []
            list_marker = '- ' if stripped.startswith('-') else '* '
            
            while i < len(lines):
                current_line = lines[i].strip()
                is_list_item = (current_line.startswith('- ') or current_line.startswith('* ') or
                               (current_line.startswith('-') and len(current_line) > 1 and current_line[1] != '-') or
                               (current_line.startswith('*') and len(current_line) > 1 and current_line[1] != '*'))
                
                if not is_list_item:
                    break
                
                if current_line.startswith('- ') or current_line.startswith('* '):
                    item_text = current_line[2:].strip()
                elif current_line.startswith('-') or current_line.startswith('*'):
                    item_text = current_line[1:].strip()
                else:
                    item_text = current_line
                
                list_items.append(item_text)
                i += 1
                
                # Check for nested items (indented with 2+ spaces)
                while i < len(lines):
                    next_line = lines[i]
                    if (next_line.startswith('  ') and 
                        (next_line.strip().startswith('- ') or next_line.strip().startswith('* '))):
                        nested_text = next_line.strip()
                        if nested_text.startswith('- ') or nested_text.startswith('* '):
                            nested_text = nested_text[2:].strip()
                        elif nested_text.startswith('-') or nested_text.startswith('*'):
                            nested_text = nested_text[1:].strip()
                        list_items.append(nested_text)
                        i += 1
                    else:
                        break
            
            list_node_items = []
            for item_text in list_items:
                text_nodes = parse_markdown_inline(item_text)
                paragraph_node = {
                    'id': str(uuid.uuid4()),
                    'type': 'PARAGRAPH',
                    'nodes': text_nodes,
                }
                list_node_items.append({
                    'id': str(uuid.uuid4()),
                    'type': 'LIST_ITEM',
                    'nodes': [paragraph_node]
                })
            
            nodes.append({
                'id': node_id,
                'type': 'BULLETED_LIST',
                'nodes': list_node_items,
            })
            continue
        
        # Ordered lists
        if re.match(r'^\d+\.\s+', stripped):
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
            
            list_node_items = []
            for item_text in list_items:
                text_nodes = parse_markdown_inline(item_text)
                paragraph_node = {
                    'id': str(uuid.uuid4()),
                    'type': 'PARAGRAPH',
                    'nodes': text_nodes,
                }
                list_node_items.append({
                    'id': str(uuid.uuid4()),
                    'type': 'LIST_ITEM',
                    'nodes': [paragraph_node]
                })
            
            nodes.append({
                'id': node_id,
                'type': 'ORDERED_LIST',
                'nodes': list_node_items,
            })
            continue
        
        # Images
        if stripped.startswith('!['):
            img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', stripped)
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
            continue
        
        # Regular paragraph
        para_lines = [stripped]
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
                next_line.startswith('```') or
                re.match(r'^(---+|\*\*\*|___+)$', next_line) or
                re.match(r'^\d+\.\s+', next_line)):
                break
            para_lines.append(next_line)
            i += 1
        
        para_text = ' '.join(para_lines)
        text_nodes = parse_markdown_inline(para_text)
        
        if text_nodes:
            nodes.append({
                'id': node_id,
                'type': 'PARAGRAPH',
                'nodes': text_nodes,
            })
    
    # Ensure at least one node exists
    if not nodes:
        nodes.append({
            'id': str(uuid.uuid4()),
            'type': 'PARAGRAPH',
            'nodes': [{
                'id': str(uuid.uuid4()),
                'type': 'TEXT',
                'nodes': [],
                'textData': {
                    'text': content[:500] if content else "This is a post from ALwrity.",
                    'decorations': []
                }
            }],
        })
    
    return {'nodes': nodes}
