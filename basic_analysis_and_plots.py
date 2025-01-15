import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
import streamlit as st

def load_and_preprocess(file):
    try:
        if file.name.endswith('.csv'):
            data = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            data = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file type. Please upload a .csv or .xlsx file.")
        
        st.write("Dataset Loaded Successfully")
        st.write("Dataset Info:")
        st.write(data.info())
        
        numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
        categorical_cols = data.select_dtypes(include=['object']).columns
        
        imputer_numeric = SimpleImputer(strategy='mean')
        data[numeric_cols] = imputer_numeric.fit_transform(data[numeric_cols])
        st.write("Missing Values Handled for Numerical Columns")
        
        imputer_categorical = SimpleImputer(strategy='most_frequent')
        data[categorical_cols] = imputer_categorical.fit_transform(data[categorical_cols])
        st.write("Missing Values Handled for Categorical Columns")
        
        label_encoder = LabelEncoder()
        for col in categorical_cols:
            data[col] = label_encoder.fit_transform(data[col])
        st.write("Categorical Variables Encoded")
        
        scaler = StandardScaler()
        data[numeric_cols] = scaler.fit_transform(data[numeric_cols])
        st.write("Data Standardized")

        return data
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def basic_visualizations(data):
    st.write("### Basic Visualizations")
    numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = data.select_dtypes(include=['object']).columns
    
    if st.checkbox('Show Scatter Plot'):
        if len(numeric_cols) > 1:
            st.write("#### Scatter Plot")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.scatterplot(x=data[numeric_cols[0]], y=data[numeric_cols[1]], ax=ax)
            st.pyplot(fig)
    
    if st.checkbox('Show Line Plot'):
        if len(numeric_cols) > 1:
            st.write("#### Line Plot")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(x=data[numeric_cols[0]], y=data[numeric_cols[1]], ax=ax)
            st.pyplot(fig)
    
    if st.checkbox('Show Bar Plot'):
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                st.write(f"#### Bar Plot of {col}")
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.countplot(data[col], ax=ax)
                plt.xticks(rotation=45)
                st.pyplot(fig)

    if st.checkbox('Show Box Plot'):
        if len(numeric_cols) > 1:
            st.write("#### Box Plot")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=data[numeric_cols[0]], ax=ax)
            st.pyplot(fig)

    if st.checkbox('Show Histogram with KDE'):
        if len(numeric_cols) > 0:
            st.write("#### Histogram with KDE")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(data[numeric_cols[0]], kde=True, ax=ax)
            st.pyplot(fig)

def advanced_visualizations(data):
    st.write("### Advanced Visualizations")
    numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
    if st.checkbox('Show Correlation Heatmap'):
        if len(numeric_cols) > 1:
            st.write("#### Correlation Heatmap")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(data[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
    
    if st.checkbox('Show PCA (2 Components)'):
        pca = PCA(n_components=2)
        pca_components = pca.fit_transform(data[numeric_cols])
        pca_df = pd.DataFrame(data=pca_components, columns=['PC1', 'PC2'])
        st.write("#### PCA - 2 Components")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x=pca_df['PC1'], y=pca_df['PC2'], ax=ax)
        st.pyplot(fig)

    if st.checkbox('Show Violin Plot'):
        if len(numeric_cols) > 1:
            st.write("#### Violin Plot")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.violinplot(x=data[numeric_cols[0]], y=data[numeric_cols[1]], ax=ax)
            st.pyplot(fig)

    if st.checkbox('Show Pairplot'):
        if len(numeric_cols) > 2:
            st.write("#### Pairplot")
            sns.pairplot(data[numeric_cols])
            st.pyplot()

def plotly_visualizations(data):
    st.write("### Plotly Visualizations")
    numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = data.select_dtypes(include=['object']).columns
    
    if st.checkbox('Show Scatter Plot with Plotly'):
        if len(numeric_cols) > 1:
            st.write("#### Scatter Plot with Plotly")
            fig = px.scatter(data, x=numeric_cols[0], y=numeric_cols[1], title="Scatter Plot")
            st.plotly_chart(fig)

    if st.checkbox('Show Line Plot with Plotly'):
        if len(numeric_cols) > 1:
            st.write("#### Line Plot with Plotly")
            fig = px.line(data, x=numeric_cols[0], y=numeric_cols[1], title="Line Plot")
            st.plotly_chart(fig)

    if st.checkbox('Show Box Plot with Plotly'):
        if len(numeric_cols) > 0:
            st.write("#### Box Plot with Plotly")
            fig = px.box(data, y=numeric_cols[0], title="Box Plot")
            st.plotly_chart(fig)

    if st.checkbox('Show Histogram with Plotly'):
        if len(numeric_cols) > 0:
            st.write("#### Histogram with Plotly")
            fig = px.histogram(data, x=numeric_cols[0], title="Histogram")
            st.plotly_chart(fig)

    if st.checkbox('Show Correlation Heatmap with Plotly'):
        if len(numeric_cols) > 1:
            st.write("#### Heatmap with Plotly")
            fig = px.imshow(data[numeric_cols].corr(), title="Correlation Heatmap")
            st.plotly_chart(fig)

    if st.checkbox('Show Violin Plot with Plotly'):
        if len(numeric_cols) > 1:
            st.write("#### Violin Plot with Plotly")
            fig = px.violin(data, y=numeric_cols[0], box=True, title="Violin Plot")
            st.plotly_chart(fig)

def generate_report(data):
    st.write("### Generating Report...")
    report = {
        "Dataset Info": data.info(),
        "Summary Statistics": data.describe(),
        "Missing Values": data.isnull().sum(),
        "Correlation Matrix": data.corr()
    }
    data.to_csv("processed_data.csv", index=False)
    st.write("Processed Data Saved as 'processed_data.csv'")

    return report

def main():
    st.title("Data Analysis and Visualization Tool")
    
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        data = load_and_preprocess(uploaded_file)
        
        if data is not None:
            basic_visualizations(data)
            advanced_visualizations(data)
            plotly_visualizations(data)
            generate_report(data)

if __name__ == "__main__":
    main()
