✈️ **Airlines Deployment Project**

Airlines Deployment is a comprehensive machine learning and deep learning platform for the Canadian airline dataset, designed to predict, analyze, and optimize airline operations and customer experience.

The project combines ML modeling, DL tasks, Flask-based deployment, chatbots, OCR processing, and Power BI dashboards to provide a complete data-driven airline management solution.

🚀 **Key Features**
🧠 **Machine Learning (ML)**

Customer Lifetime Value (CLV) Prediction – predict high-value customers for targeted marketing

Churn Prediction – identify customers likely to leave the airline

Delay Prediction – predict flight delays using ticket and flight data

Engine Health Prediction – detect potential aircraft engine issues

Unsupervised Clustering:

Delay Clusters – group flights by delay patterns

Customer Segmentation – cluster passengers based on behavior

Aircraft Analysis – cluster aircraft types and usage

🤖 **Deep Learning (DL)**

OCR + Regex Ticket Reading – extract flight ticket information for ML models

BERT NLP Comment Classification – categorize customer comments (positive, negative, neutral) for admin review

Client-Facing NLP Chatbot – powered by Whisper (voice) + GPT, answering airline-specific questions

Integration of ML/DL for Admin – monitor comment categories, customer segmentation, CLV, and delay clusters

💻 **Deployment & Interface**

Flask Framework – login, forms, and deployment for client and admin interfaces

Client-Side DL Features – analyze tickets and predict delays using OCR + ML models

Admin Dashboard – monitor ML outputs (CLV, churn, delay clusters, flight clusters)

Power BI Integration:

Accueil Page – project overview

Customer Page – detailed customer information

CLV Page – visualize customer lifetime value predictions

Churn Page – visualize churn predictions

Profitability Page & Ratio Page – monitor airline KPIs

🧩 **System Architecture**
| **Component**             | **Description**                                           |
|---------------------------|-----------------------------------------------------------|
| **Frontend**              | Flask templates, HTML, CSS, JS                             |
| **Backend**               | Flask, Python ML/DL pipelines                              |
| **Database**              | SQL / CSV datasets                                        |
| **Machine Learning**      | scikit-learn, clustering, regression, classification models |
| **Deep Learning / NLP**   | OCR, Regex, BERT, Whisper, GPT                             |
| **Visualization**         | Power BI dashboards                                        |
| **Authentication & Forms** | Flask login & forms for clients/admin                     |

👤 **Personal Contribution**

_Machine Learning:_

CLV prediction

Delay cluster analysis

_Deep Learning:_

OCR and Regex ticket reading to extract flight info

Feeding OCR output into delay prediction models

_Power BI Dashboards:_

CLV page and Customer page development

Integration of ML predictions into dashboard visualizations

_Deployment:_

Flask-based forms, login, and admin interface

🎯 **Project Objective**

The project aims to combine ML, DL, NLP, and visualization to create a data-driven airline operations platform, improving decision-making, customer experience, and operational efficiency.
