import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from lib.ai_marketing_tools.ai_backlinker.ai_backlinking import find_backlink_opportunities, compose_personalized_email


# Streamlit UI function
def backlinking_ui():
    st.title("AI Backlinking Tool")

    # Step 1: Get user inputs
    keyword = st.text_input("Enter a keyword", value="technology")

    # Step 2: Generate backlink opportunities
    if st.button("Find Backlink Opportunities"):
        if keyword:
            backlink_opportunities = find_backlink_opportunities(keyword)

            # Convert results to a DataFrame for display
            df = pd.DataFrame(backlink_opportunities)

            # Create a selectable table using st-aggrid
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
            gridOptions = gb.build()

            grid_response = AgGrid(
                df,
                gridOptions=gridOptions,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                height=200,
                width='100%'
            )

            selected_rows = grid_response['selected_rows']

            if selected_rows:
                st.write("Selected Opportunities:")
                st.table(pd.DataFrame(selected_rows))

                # Step 3: Option to generate personalized emails for selected opportunities
                if st.button("Generate Emails for Selected Opportunities"):
                    user_proposal = {
                        "user_name": st.text_input("Your Name", value="John Doe"),
                        "user_email": st.text_input("Your Email", value="john@example.com")
                    }

                    emails = []
                    for selected in selected_rows:
                        insights = f"Insights based on content from {selected['url']}."
                        email = compose_personalized_email(selected, insights, user_proposal)
                        emails.append(email)

                    st.subheader("Generated Emails:")
                    for email in emails:
                        st.write(email)
                        st.markdown("---")

        else:
            st.error("Please enter a keyword.")
