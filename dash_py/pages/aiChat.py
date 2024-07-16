import dash
from dash import html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from langchain_community.llms import Ollama
import torch
from utils.env import sese_diagram_grammar
dash.register_page(__name__, path='/ai')
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print(device)
def instructLLAMA():
    prompt_init = '''
        You are an assistant to design processes. In particular, 
        your role is to pass from an user description of the process to the grammar defined using the python library lark.  
        Note that all process that you have to create are BPMN diagram that are single-entry-single-exit (SESE). 
        Meaning that for all nodes you have only one element in exit and one incoming.        
        There are few exceptions which are: natures or probabilistic split, choice and parallel. They have one entry but 2 exits.
        That is because the the choices and the natures represents xor decisions while parallel represents 'and', so taking both the branches.
        '''
    prompt_init += f'the grammar is {sese_diagram_grammar}. \n All the different section of the process are inserted in (). These can be nested as (T1, (T2,T3)).'    
    response = llm.invoke(prompt_init)
    chat_history.append((prompt_init, response))
    prompt_init += '''
        Here an example. 
        User: depicts a metal manufacturing process that involves cutting, milling,
        bending, polishing, depositioning, and painting a metal piece. 
        First the cutting is done. Then, I have to do both:
        - bending and then there is a nature that decides between heavy or light polishing
        - milling, then I have a choice between fine or rough deposition
        after this there is a choice between the hphs or lpls painting.
        With this choice the process is concluded. 
        The traduction is: (Cutting, ( (Bending, (HP ^ [N1]LP ) ) || ( Milling, ( FD / [C1] RD))), (HPHS / [C2] LPLS))
        Another example: 
        I have a process where at the beginnig the user has to do 5 surveys (call them S1, S2,S3, ...) alltogheter. 
        Then, Based on the answer there is a nature that send me or in a T1 or T2. After I have 2 choises to make.
        the traduction: (S1 || S2 || S3 || S4 || S5), (T1 ^ [N1] T2), (C1 / [C2] C2)
        '''
    response = llm.invoke(prompt_init)
    chat_history.append((prompt_init, response))
    print('llama instructed')
    print(chat_history)


llm = Ollama(model="llama3",num_gpu = 1)
# Initialize chat history
chat_history = []
# instructLLAMA()

layout = html.Div([
    dbc.Textarea(id='input-box', placeholder='Type your message here...'),
    html.Br(),
    dbc.Button('Send', id='send-button'),
    html.Div(id='chat-output')
])

@callback(
    Output('chat-output', 'children'),
    [Input('send-button', 'n_clicks')],
    [State('input-box', 'value')],
    prevent_initial_call=True
)
def update_output(n_clicks, prompt):
    instructLLAMA()
    if prompt:
        print(prompt)
        try:
            response = llm.invoke(prompt)
            print(f' response {response}')
            
            # Add the user's message and the assistant's response to the chat history
            chat_history.append((prompt, response))
            
            # Generate the chat history for display
            chat_display = []
            for user_msg, assistant_msg in chat_history:
                chat_display.append(html.P(f"User: {user_msg}"))
                chat_display.append(html.P(f"Assistant: {assistant_msg}"))
            
            return html.Div(chat_display)
        except Exception as e:
            return html.P(f"Error: {e}")

