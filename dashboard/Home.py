import streamlit as st

st.set_page_config(
    page_title="RailGuard: CheckUrChoo",
    page_icon="🚆",
)

# Page title
st.title("RailGuard: Check A Choo")

# Main section
st.header("Welcome!")

st.write(
    "Streamlit is an open-source Python library that makes it easy to create web apps for machine learning, data exploration, and more. With Streamlit, you can build interactive and beautiful applications with only a few lines of code."
)

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)
