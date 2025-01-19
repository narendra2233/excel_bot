import streamlit as st
import openai
import pandas as pd
import io

# Function to get the response from GPT-3 or GPT-4
def get_bot_response(user_input, excel_data=None):
    try:
        excel_data['Transaction date'] = pd.to_datetime(excel_data['Transaction date'])

        if user_input:
            # Handle requests related to the Excel data
            if "summary" in user_input.lower():
                return excel_data.describe().to_string()  # Show a statistical summary
            elif "columns" in user_input.lower():
                return f"The columns in the data are: {excel_data.columns.tolist()}"  # List the columns of the data
            elif any(keyword in user_input.lower() for keyword in ["head",'top','show','few rows']):
                return st.dataframe(excel_data.head())  # Show the first 5 rows
            elif 'rows' in user_input.lower() or 'total rows' in user_input.lower():
                return excel_data.shape[0]
            
            elif "shape" in user_input.lower():
                return str(excel_data.shape)  # Show the shape of the data
            elif "info" in user_input.lower() or 'describe' in user_input.lower():
                buffer = io.StringIO()
                excel_data.info(buf=buffer)
                return buffer.getvalue()  # Show general information about the data
            elif "transactions on" in user_input.lower():
                date_input = user_input.lower().split("transactions on")[-1].strip()  # Extract date after 'transaction on'
                specific_date = pd.to_datetime(date_input, errors='coerce')
                if specific_date:
                      filtered_data=excel_data[excel_data['Transaction date']==specific_date]
                      if filtered_data.empty:
                            return f"No Transaction found on {specific_date} ."

                      else:
                            return filtered_Data
                else:
                      "Invalid date format. Please use YYYY/MM/DD."
            else:
                # Use OpenAI's GPT model for general conversation if no file is involved
                openai.api_key = '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'  # Replace with your OpenAI API key securely
                response = openai.Completion.create(
                model="gpt-3.5-turbo",  # or "gpt-4"
                messages=[{'role':'system','content':excel_data.to_string(index=False)},
                    {"role": "user", "content": user_input}],
                max_tokens=150
                )
                bot_message = response['choices'][0]['message']['content']
                return bot_message
        else:
            user_input=st.input_text('plase enter your input.')
        
            
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit app
def main():
    # App title
    st.title("AI Chatbot with Excel File Handling")

    # Greeting message
    if "history" not in st.session_state or len(st.session_state.history) == 0:
       st.markdown("""
       **Hello and welcome!** 👋 I'm your AI-powered assistant, ready to help you explore and interact with your data.

      🗂️ **Upload your Excel file** below and ask me anything about the data! Whether you want to know the summary, columns, or even details like the shape     of your dataset – I'm here to assist.

      Let’s get started! Feel free to upload your file and ask away.
      """)

    # Allow user to upload an Excel file (only accepts xlsx, xls)
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    excel_data = None

    if uploaded_file is not None:
        # Load the Excel file into a pandas DataFrame
        excel_data = pd.read_excel(uploaded_file)

        # Show a success message after file is uploaded
        st.success("Excel file loaded successfully!")

        # Optionally, display the first few rows of the data
        st.write("Preview of the data:")
        st.write(excel_data.head())
        
        # Initialize session state history if not already
        if "history" not in st.session_state:
            st.session_state.history = []

    # Input box for the user to type a message, but only if a file is uploaded
    if uploaded_file is not None:

        # Create a unique key based on the length of the history (dynamic)
        input_key = f"user_input_{len(st.session_state.history)}"  # Change the key dynamically for each message

        # Create the chat history first
        for message in st.session_state.history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Bot:** {message['content']}")

        # Input box for user message placed below the chat history
        user_input = st.text_input("Ask about the data:", key=input_key)

        if user_input:
            # Add user input to chat history
            st.session_state.history.append({"role": "user", "content": user_input})

            # If the user wants to exit, end the chat
            if "exit" in user_input.lower() or "thank you" in user_input.lower():
                st.session_state.history.append({"role": "bot", "content": "Goodbye! Feel free to come back anytime."})
                st.stop()  # Stop the app from further execution

            # Get the chatbot's response (either based on the Excel data or general response)
            bot_response = get_bot_response(user_input, excel_data)

            # Add bot response to chat history
            st.session_state.history.append({"role": "bot", "content": bot_response})

            # After the response is added, update the chat history again and show the new input box
            for message in st.session_state.history:
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**Bot:** {message['content']}")

            # Create a new text box for the next user input (clear the old one by updating key)
            st.text_input("Ask about the data:", key=f"user_input_{len(st.session_state.history)}")

    else:
        # If no file is uploaded, ask the user to upload one
        st.info("Please upload an Excel file to start chatting with the bot.")

if __name__ == "__main__":
    main()
