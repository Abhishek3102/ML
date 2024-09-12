# from langchain_community.llms import OpenAI
# from dotenv import load_dotenv

# load_dotenv()                                                     PURANA CODE


# def generate_pet_name():
#     llm = OpenAI(temperature=0.7)

#     name = llm("I have a pet dog pet and I want a cool name for it. Suggest me five cool Indian names for dog.")

#     return name 
    
# if __name__ == "__main__":
#     print(generate_pet_name())
      


from langchain_openai import OpenAI  # Updated import for OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType

load_dotenv()

def generate_pet_name(animal_type, pet_color):
    llm = OpenAI(temperature=0.7)

    prompt_template_name = PromptTemplate(
        input_variables=['animal_type','pet_color'],
        template="I have a {animal_type} pet and I want a cool name for it. {pet_color} in color. Suggest me five cool male japanese anime names for pet."
    )

    # Use invoke instead of __call__
    name = llm.invoke("I have a pet dog and I want a cool name for it. Suggest me five cool Indian names for dog.")
    name_chain = LLMChain(llm=llm, prompt=prompt_template_name, output_key="pet_name")
    response = name_chain.invoke({'animal_type': animal_type, 'pet_color': pet_color})

    return response




if __name__ == "__main__":
    # langchain_agent()
      print(generate_pet_name("cat","blue"))


     

