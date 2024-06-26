import streamlit as st
from PIL import Image
import json
import urllib.request
import ssl

# Set the URL of the API endpoint
API_URL = "http://4.234.24.55:80/api/v1/service/gpu-rn50/score"

# Display the logo
image = Image.open("nhg_logo.png")
st.image(image, width=100)

# Streamlit app title
st.title("Annual Visits - Tenant's Journey")

# Input payment reference
ref_tenant = 3131678
# input_payment_reference = st.text_input(label="Enter Payment Reference (Examples: 50120515, 3131678, 53517814)", value=ref_tenant)


# Set a session state key to check if the user has already entered a value
if 'input_payment_reference' not in st.session_state:
    st.session_state.input_payment_reference = ref_tenant

# Get the user input and update the session state
input_payment_reference = st.text_input(
    label="Enter Payment Reference (Examples: 50120515, 3131678, 53517814)",
    value=st.session_state.input_payment_reference
)

# Update the session state with the user input
st.session_state.input_payment_reference = input_payment_reference

# Display the entered payment reference
st.write(f"Payment Reference: {input_payment_reference}")


# Initialize session ID in Streamlit session state
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = None

def make_request(action, data):

    request_data = {
        "action": action,
        "data": data
    }

    if st.session_state['session_id']:
        request_data['session_id'] = st.session_state['session_id']

    body = str.encode(json.dumps(request_data))

    headers = {'Content-Type':'application/json'}

    req = urllib.request.Request(API_URL, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result_tmp = json.loads(response.read().decode('utf-8'))
        result = json.loads(result_tmp)
        st.session_state['session_id'] = result.get('session_id', st.session_state['session_id'])
        return result
    except urllib.error.HTTPError as error:
        st.error(f"The request failed with status code: {error.code}")
        error_info = error.info()
        error_details = error.read().decode("utf8", 'ignore')
        st.error(f"Error details: {error_info}\n{error_details}")
        return None

def load_my_tenant(input_payment_reference):
    result = make_request("load_tenant", input_payment_reference)
    if result:
        st.session_state.completed_issues = result.get("completed_issues", "No data available")
        st.session_state.completed_repairs = result.get("completed_repairs", "No data available")
        st.session_state.inprogress_issues = result.get("inprogress_issues", "No data available")
        st.session_state.inprogress_repairs = result.get("inprogress_repairs", "No data available")
        st.session_state.inprogress_info = result.get("inprogress_info", "No data available")
        st.session_state.completed_info = result.get("completed_info", "No data available")
        print(result.get("session_id_list", "No data available"))

def generate_summary(action, ratio_key, summary_key):
    ratio = st.session_state[ratio_key] / 100
    result = make_request(action, ratio)
    if result:
        st.session_state[summary_key] = result.get("summary", "No data available")

def generate_in_rep_sum():
    generate_summary("generate_in_rep_sum", "in_repair_sum_opt", "inprogress_repairs_summary")

def generate_in_issue_sum():
    generate_summary("generate_in_issue_sum", "in_issue_sum_opt", "inprogress_issues_summary")

def generate_com_rep_sum():
    generate_summary("generate_com_rep_sum", "com_rep_sum_opt", "completed_repairs_summary")

def generate_com_issue_sum():
    generate_summary("generate_com_issue_sum", "com_issue_sum_opt", "completed_issues_summary")

def generate_legacy_sum():
    generate_summary("generate_legacy_sum", "leg_sum_opt", "legacy_summary")

def generate_inprogress_summaries():
    generate_in_rep_sum()
    generate_in_issue_sum()

def generate_completed_summaries():
    generate_com_rep_sum()
    generate_com_issue_sum()

def generate_all_summaries():
    generate_completed_summaries()
    generate_inprogress_summaries()
    generate_legacy_sum()

# Button to load tenant data
if st.button("Load tenant", key="load_tenant_button"):
    load_my_tenant(input_payment_reference)

# Button to generate all summaries
if st.button("Generate all summaries"):
    generate_all_summaries()

# Tabs for different functionalities
inprogress_summary_tab, completed_summary_tab, legacy_tab, qa_tab = st.tabs(["Inprogress Summaries", "Completed Summaries", "Legacy Info", "Question answering"])

# In-progress summaries tab
with inprogress_summary_tab:
    st.button("Generate Summaries", key="gen_sum_in", on_click = generate_inprogress_summaries)
    st.markdown("**__Inprogress repairs__**")
    st.write(st.session_state.get('inprogress_repairs_summary', 'No data available'))
    with st.expander("summary options"):
        st.slider("Provide a length of your summary", value=20, min_value=0, max_value=100, step=1, key="in_repair_sum_opt")
        st.button("Regenerate summary", key="regen_in_repair", on_click = generate_in_rep_sum)
    with st.expander("See original content"):
        st.write(st.session_state.get('inprogress_repairs', 'No data available'))

    st.write("__Inprogress Issues__")
    st.write(st.session_state.get('inprogress_issues_summary', 'No data available'))
    with st.expander("summary options"):
        st.slider("Provide a length of your summary", value=20, min_value=0, max_value=100, step=1, key="in_issue_sum_opt")
        st.button("Regenerate summary", key="regen_sum_in_issue", on_click = generate_in_issue_sum)
    with st.expander("See original content"):
        st.write(st.session_state.get('inprogress_issues', 'No data available'))

# Completed summaries tab
with completed_summary_tab:
    st.button("Generate Summaries", key="gen_com_sum", on_click = generate_completed_summaries)
    st.write("__Completed repairs__")
    st.write(st.session_state.get('completed_repairs_summary', 'No data available'))
    with st.expander("summary options"):
        st.slider("summary length", value=20, min_value=0, max_value=100, step=1, key="com_rep_sum_opt")
        st.button("Regenerate summary", key="com_rep_sum", on_click = generate_com_rep_sum)
    with st.expander("See original content"):
        st.write(st.session_state.get('completed_repairs', 'No data available'))

    st.write("__Completed issues__")
    st.write(st.session_state.get('completed_issues_summary', 'No data available'))
    with st.expander("summary options"):
        st.slider("summary length", value=20, min_value=0, max_value=100, step=1, key="com_issue_sum_opt")
        st.button("Regenerate summary", key="com_issue_sum", on_click = generate_com_issue_sum)
    with st.expander("See original content"):
        st.write(st.session_state.get('completed_issues', 'No data available'))

# Legacy info tab
with legacy_tab:
    st.button("Generate Summary", key="gen_leg_sum", on_click = generate_legacy_sum)
    st.write("__Legacy Summary__")
    st.write(st.session_state.get('legacy_summary', 'No data available'))
    with st.expander("summary options"):
        st.slider("summary length", value=20, min_value=0, max_value=100, step=1, key="leg_sum_opt")
        st.button("Regenerate summary", key="regen_leg_sum", on_click = generate_legacy_sum)
    with st.expander("See original content"):
        st.write(st.session_state.get('legacy_info', 'No data available'))

# Question answering tab
def ask(input_question, context):
    result = make_request("ask", {"question": input_question, "context": context})
    if result:
        st.session_state.answer = result.get("answer", "No answer available")

with qa_tab:
    st.radio("Completed or inprogress?", ["completed", "inprogress"], horizontal=True, key="context")
    input_question = st.text_input(label="What do you want to ask?", value="", key="question")
    if st.button("Ask", key="ask"):
        ask(input_question, st.session_state.context)
    st.write(st.session_state.get('answer', "Ask me anything."))



def delete_session():
    if st.session_state['session_id']:
        result = make_request("session_id_del", {"session_id": st.session_state['session_id']})
        if result:
            print(result)

def delete_all_sessions():
    result = make_request("session_id_all_del", "")
    if result:
        print(result)

with st.expander("Restricted Area! Don't Touch Me!"):
    st.button("Delete This Session", key="del_session", on_click = delete_session)
    st.button("Delete All Sessions", key="del_sessions", on_click = delete_all_sessions)