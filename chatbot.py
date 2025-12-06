
from openai import OpenAI
import pdfplumber

# a financial chatbot where you can upload a pdf, set a goal saying GOAL: xyz, or just asking a ?


client = OpenAI(
    api_key = "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")


# PDF EXTRACTOR 
def extract_text(path):
    # Initialize an empty string to store all text
    text = ""
    
    # Open the PDF file using pdfplumber
    with pdfplumber.open(path) as pdf:
        # Loop through every page in the PDF, and for every page ...
        for page in pdf.pages:
            # Extract text from the current page
            t = page.extract_text()
            
            # If text exists on the page, append it to the full text
            if t:
                text += t + "\n"
    
    # Return the extracted text for use in the chatbot
    return text



# AI System that uses our PDF text
def financial_chatbot():
    # System instructions for how the AI should behave
    system_prompt = """
You are a friendly and knowledgeable financial assistant.
You help users with budgeting, saving, debt, credit score, and good financial habits.
You can also analyze uploaded bank statements, compare spending to goals,
and suggest improvements.
Always respond in clear, supportive language.
"""
    
    # This stores the upcoming entire conversation for the AI to reference
    chat_history = [{"role": "system", "content": system_prompt}]
    
    # Stores the extracted text from an uploaded PDF
    uploaded_pdf_text = None
    
    # Stores the user's financial goal once provided
    current_goal = None

    # print instructions for the user
    print("\nFinancial Chatbot started! Type STOP to exit.\n")
    print("Start a conversation by asking for financial advice.")
    print("Or upload a PDF to discuss financial data using:  UPLOAD: path/to/file.pdf\n")




    # Main chatbot loop that keeps running until STOP is typed
    while True:
        user_input = input("You: ").strip()

        # --- exiting ---
        if user_input.upper() == "STOP":
            print("Conversation ended.")
            return chat_history

        
        # --- PDF Upload Handling ---
        if user_input.startswith("UPLOAD:"):
            # get the file path after "UPLOAD:"
            pdf_path = user_input.replace("UPLOAD:", "").strip()
            
            # Call func to read PDF content
            uploaded_pdf_text = extract_text(pdf_path)

            # if worked, then let user know
            print("\nAssistant: PDF uploaded successfully!")
            print("(You can now chat normally or set a goal with: GOAL: <your goal>)\n")
            continue

        # --- Goal Setting ---
        if user_input.startswith("GOAL:"):
            # if user writes GOAL: with no PDF sent beforehand
            if uploaded_pdf_text is None:
                print("\nAssistant: You must upload a PDF first.\n")
                continue

            # Extract the user’s financial goal text
            current_goal = user_input.replace("GOAL:", "").strip()

            # Build the prompt given to the AI with:
            # - The extracted PDF text
            # - The user’s goals
            # - Instructions on how the AI should analyze that info
            analysis_prompt = f"""
I uploaded a bank statement. Here is the extracted text:

{uploaded_pdf_text}

My financial goals are: {current_goal}


You are a helpful and knowledgeable financial guidance assistant. Your job is to answer the user’s questions and provide clear, practical financial advice based on the information they provide.

If the user has uploaded a bank statement analysis or monthly spending report, use that information to make your recommendations more accurate. If no data is available, rely entirely on the user’s manually entered information.

When responding to the user:

1. Always speak clearly and use simple, friendly language.
2. Provide actionable steps instead of vague suggestions.
3. Base your advice strictly on the data or details provided by the user.
4. Never assume information that has not been given.
5. If you need more details to give accurate advice, ask the user follow-up questions.
6. Do not provide legal, tax, or investment guarantees. Focus on budgeting, spending habits, and personal finance best practices.

For every answer you generate, follow this structure:

A. **Summary of User’s Question**  
   Briefly restate what the user is asking to show understanding.

B. **Analysis**  
   - Use uploaded spending data if available.  
   - Use the user’s stated input and goals.  
   - Identify patterns, problems, or key points.

C. **Actionable Recommendations**  
   Provide 2–5 specific steps the user can take.  
   The advice should be practical and personalized.

D. **Optional Follow-Up Question**  
   If needed, ask for more information to give deeper insight.

Your goal is to help the user clearly understand their financial situation and make informed decisions.
"""
            # Save this to chat history we made earlier
            chat_history.append({"role": "user", "content": analysis_prompt})

            # Send the GOAL message with instructions to the AI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=chat_history
            )

            # Extract the assistant’s text output
            assistant_response = response.choices[0].message.content
            
            # Print the response
            print("\nAssistant:", assistant_response, "\n")

            # Add the AI response to chat history for more context if user continues chat
            chat_history.append({"role": "assistant", "content": assistant_response})
            continue



        # --- Normal Chat Behavior ---
        # just use the user input if it doesnt start with GOAL: or STOP
        normal_prompt = user_input

        # If a PDF was uploaded before, attach some helpful context
        if uploaded_pdf_text:
            normal_prompt += f"""

(Helpful Context: The user has uploaded a bank statement. Here is its extracted text:
{uploaded_pdf_text[:4500]}
...)
"""

        # Add the messages to chat history
        chat_history.append({"role": "user", "content": normal_prompt})

        # Ask the AI for a response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=chat_history
        )

        # Extract text from the AI response
        assistant_response = response.choices[0].message.content
        
        # Print the response
        print("\nAssistant:", assistant_response, "\n")

        # Save to chat history
        chat_history.append({"role": "assistant", "content": assistant_response})


# Start the financial chatbot
financial_chatbot()
