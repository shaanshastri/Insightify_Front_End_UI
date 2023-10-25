import openai
from metadata import generate_synapse_ddls
from fetch_data import fetch_data_synapse
from langchain_experimental.sql import SQLDatabaseChain
from langchain.utilities import SQLDatabase
from langchain.chat_models import AzureChatOpenAI
from langchain.chains import create_sql_query_chain
import os
from sqlalchemy.engine import URL


def convert_nlp_to_sql_poc(prompt_text):
    # openai.api_key = "c4b435efc4a2442880527e59169438a8"
    # openai.api_base = "https://cog-6sbix7titqeb2.openai.azure.com/"
    # openai.api_type = 'azure'
    # openai.api_version = '2023-07-01-preview'
    # deployment_name = 'davinci'
    # database_name = "GenAI"

    serverless_connection_string = ('Driver={ODBC Driver 18 for SQL Server};Server=tcp:synw-infra-int-dev-ondemand.sql'
                                    '.azuresynapse.net,1433;Database=GenAI;Uid=masterdummy;Pwd={'
                                    '!pass@123};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    # metadata_adv = generate_synapse_ddls(serverless_connection_string, database_name)

    # full_prompt = f"""
    # You are expert SQL developer, write a SQL query for the text enclosed within "---" 
    # ---{str(prompt_text)}---.\n
    # Use the table data definition language (ddl) enclosed within "---" below ensuring the query is specific to column and table names.
    # ---{str(metadata_adv)}--- \n
    # The response should only be the SQL query without any explanation. \n
    # """
    # # If the query is not linked to the tables in the above ddls, output that no such table is available."""
    # response = openai.Completion.create(
    #     engine=deployment_name,
    #     prompt=full_prompt,
    #     temperature=0,
    #     max_tokens=600,
    #     top_p=1.0,
    #     frequency_penalty=0.0,
    #     presence_penalty=0.0,
    #     stop=["#", ";"])

    # # print(full_prompt)
    # answer = response.choices[0].text.strip()
    # final_ans = answer.replace("'", "").replace("?", "").replace("<|im_end|>", "")
    # try:
    #     out = fetch_data_synapse(serverless_connection_string, final_ans)
    #     return final_ans, out
    # except Exception as e:
    #     print(f"Error: {str(e)}")
    my_uid = "masterdummy_2"
    my_pwd = "!pass@123"
    my_host = "tcp:synw-infra-int-dev-ondemand.sql.azuresynapse.net,1433"
    my_db = "GenAI_v2"
    my_odbc_driver = "ODBC Driver 18 for SQL Server"

    connection_url = URL.create(
        "mssql+pyodbc",
        username=my_uid,
        password=my_pwd,
        host=my_host,
        database=my_db,  # required; not an empty string
        query={"driver": my_odbc_driver},
    )
    # print(connection_url)

    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_VERSION"] = '2023-07-01-preview'
    os.environ["OPENAI_API_BASE"] = "https://cog-6sbix7titqeb2.openai.azure.com/"
    os.environ["OPENAI_API_KEY"] = "c4b435efc4a2442880527e59169438a8"

    db = SQLDatabase.from_uri(connection_url)

    #setting Azure OpenAI env variables

    llm = AzureChatOpenAI(deployment_name="davinci", temperature=0, max_tokens=4000)
    # db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True)

    # from langchain.chat_models import ChatOpenAI
    chain = create_sql_query_chain(llm, db)
    response = chain.invoke({"question":"Who are the customers buying yellow colored product in january."})
    out = fetch_data_synapse(serverless_connection_string, response)
    return response, out

