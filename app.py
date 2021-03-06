#carregando as bibliotecas
import pandas as pd
import streamlit as st
from minio import Minio
import pickle
import joblib
import matplotlib.pyplot as plt
from pycaret.classification import load_model, predict_model

#Baixando os aquivos do Data Lake
# client = Minio(
        #"localhost:9000",
        #access_key="minioadmin",
        #secret_key="minioadmin",
        #secure=False
    #)

#modelo de classificacao,dataset e cluster.
#client.fget_object("curated","model.pkl","model.pkl")
#client.fget_object("curated","ml_dataset.csv","ml_dataset.csv")
#client.fget_object("curated","cluster.joblib","cluster.joblib")

var_model = "model"
var_model_cluster = "cluster.joblib"
var_dataset = "ml_dataset.csv"

#carregando o modelo treinado.
model = load_model(var_model)
model_cluster = joblib.load(var_model_cluster)

#carregando o conjunto de dados.
dataset = pd.read_csv(var_dataset)

print (dataset.head())

# título
st.title("Human Resource Analytics")

# subtítulo
st.markdown("**Prévia do Dataset de funcionários**")

# imprime o conjunto de dados usado
st.dataframe(dataset.head())

# grupos de empregados.
kmeans_colors = ['green' if c == 0 else 'red' if c == 1 else 'blue' for c in model_cluster.labels_]

st.sidebar.subheader("Defina os atributos do empregado para predição de turnover")

# mapeando dados do usuário para cada atributo
satisfaction = st.sidebar.number_input("Nota de satisfação", value=0.00, step=0.10, format="%.2f")
evaluation = st.sidebar.number_input("Nota de avaliação", value=0.00, step=0.01, format="%.2f")
averageMonthlyHours = st.sidebar.number_input("Média de trabalho mensal", value=0, step=1)
projectCount = st.sidebar.number_input("Número de projetos", value=0, step=1)
yearsAtCompany = st.sidebar.number_input("Anos de carreira", value=0, step=1)

# inserindo um botão na tela
btn_predict = st.sidebar.button("Realizar Classificação")

# verifica se o botão foi acionado
if btn_predict:
    data_teste = pd.DataFrame()
    data_teste["satisfaction"] = [satisfaction]
    data_teste["evaluation"] =	[evaluation]    
    data_teste["averageMonthlyHours"] = [averageMonthlyHours]
    data_teste["projectCount"] = [projectCount]
    data_teste["yearsAtCompany"] = [yearsAtCompany]

    #realiza a predição
    result = predict_model(model, data=data_teste)

    # subtítulo
    st.markdown("**Resultado:**")
    data = pd.DataFrame(result)

    if data.loc[0,'Label'] == 1:
        st.header("Este colaborador poderá sair da empresa.")
    else:
        st.header("Este colaborador permanecerá na empresa.")

    st.write(data)
    
    fig = plt.figure(figsize=(10, 6))
    plt.scatter( x="satisfaction"
                ,y="evaluation"
                ,data=dataset[dataset.turnover==1],
                alpha=0.25,color = kmeans_colors)

    plt.xlabel("Satisfaction")
    plt.ylabel("Evaluation")

    plt.scatter( x=model_cluster.cluster_centers_[:,0]
                ,y=model_cluster.cluster_centers_[:,1]
                ,color="black"
                ,marker="X",s=100)
    
    plt.scatter( x=[satisfaction]
                ,y=[evaluation]
                ,color="yellow"
                ,marker="X",s=300)

    plt.title("Grupos de Empregados - Satisfação vs Avaliação.")
    plt.show()
    st.pyplot(fig)