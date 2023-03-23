import io
import os
import subprocess

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from st_aggrid import AgGrid

# Create the sidebar
st.set_page_config(layout="wide")

# Add an optional logo
# logo = Image.open(r"...\My_Logo.png")
# st.sidebar.image(logo, width=120)

# Add the expander to provide some information about the app
with st.sidebar.expander("About the App"):
    st.write(
        """
        This interactive project management App was built using Streamlit.
        You can use the app to easily and quickly generate a Gannt chart for any project plan and management purposes.
        \n\n
        You can edit the project plan within the app and instantly generate and update the Gantt chart.
        You can also export the Gantt chart to png file and share it with your team very easily.
    """
    )

# Create a user feedback section to collect comments and ratings from users
with st.sidebar.form(key="columns_in_form", clear_on_submit=True):
    st.write("Please help us improve!")
    # horizontal radio buttons
    st.write(
        """
        <style>
            div.row-widget.stRadio > div{
                flex-diection: row;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )
    rating = st.radio("Please rate the app", [str(i) for i in range(1, 6)], index=4)
    text = st.text_input(label="Please leave your feedback here")
    submitted = st.form_submit_button("Submit")
    if submitted:
        # FIXME: This is pretty sloppy and could be condensed
        st.write("Thanks for your feedback!")
        st.markdown("Your Rating:")
        st.markdown(rating)
        st.markdown("Your Feedback:")
        st.markdown(text)

# Create the main interface
# add an app title and use css to style title
st.markdown(
    """
    <style>
        .font {
            font-size: 30px;
            font-family: 'Cooper Black';
            color: #ff9633;
        }
    </style>
""",
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="font">Upload your project plan file and generate a Gantt chart instantly</p>'
)

# Add a template screenshot as an example
st.subheader("Step 1: Download the project plan template")
# FIXME: Again where are these images...
# image = Image.open(r'...\example.png')
# st.image(image, caption='Make sure you use the same column names as the template')


# Allow users to download the template
@st.cache
def convert_df(df):
    return df.to_csv().encode("utf-8")


df = pd.read_csv(r"...\template.csv")
csv = convert_df(df)
st.download_button(
    label="Download Template",
    data=csv,
    file_name="project_template.csv",
    mime="text/csv",
)

# Add a file uploader to allow users to upload their project plan file
st.subheader("Step 2: Upload your project plan file")
uploaded_file = st.file_uploader(
    "Fill out the project plan template and upload your file here. After you upload the file, you can edit your project plan within the app."
)
if uploaded_file is not None:
    tasks = pd.read_csv(uploaded_file)
    tasks["start"] = tasks["start"].astype("datetime64")
    tasks["finish"] = tasks["finish"].astype("datetime64")

    grid_response = AgGrid(tasks, editable=True, height=300, width="100%")
    updated = grid_response["data"]
    df = pd.DataFrame(updated)

    st.subheader("Step 3: Generate the Gantt chart")
    options = st.selectbox("View Gantt Chart by:", ["Team", "Completion %"], index=0)
    if st.button("Generate Gantt Chart"):
        fig = px.timeline(
            df,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color=options,
            hover_name="Task Description",
        )
        # If not specified as `reversed` the tasks will be listed from bottom up
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            title="Project Plan Gantt Chart",
            hoverlabel_bgcolor="#daeeed",
            bargap=0.2,
            height=600,
            xaxis_title="",
            yaxis_title="",
            # center title
            title_x=0.5,
            xaxis=dict(
                tickfont_size=15,
                tickangle=270,
                rangesliver_visible=True,
                # place the tick labels on the top of the chart
                side="top",
                showgrid=True,
                zeroline=True,
                showline=True,
                showticklabels=True,
                tickformat="%x\n",
            ),
        )
        fig.update_xaxes(
            tickangle=0, tickfont=dict(family="Rockwell", color="blue", size=15)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(
            "Bonus: Export the interactive Gantt Chart to HTML and share with others!"
        )

        def download_chart() -> bytes:
            buffer = io.StringIO()
            fig.write_html(buffer, include_plotlyjs="cdn")
            html_bytes = buffer.getvalue().encode()
            return html_bytes

        st.download_button(
            label="Export to HTML",
            data=(lambda: download_chart),
            file_name="Gantt.html",
            mime="text/html",
        )
    else:
        st.write("---")
else:
    st.warning("You need to upload a csv file.")


# TODO: This kinda works but is pretty confusing...
def main():
    filename = os.getcwd() + os.sep + __name__.replace(".", os.sep) + ".py"
    args = ["streamlit", "run", filename, "--server.headless", "true"]
    process = subprocess.Popen(args)
    print(process)


if __name__ == "__main__":
    main()
