# Infosys-Intelligent-Assistant
**Infosys Intelligent Assistant (IIA)** is developed using advanced AI/ML capabilities to significantly increase the productivity of ticket management and resolution process. IIA is trained using historical ticket dump on machine learning algorithms to predict the various fields in the ticket helps in effective ticket management and resolution.

In application maintenance services, teams perform several non-value-adding tasks manually which can lower the productivity of the entire process like reworking tickets after incorrect mapping, validating the information manually to enrich the ticket, expending efforts on known issues due to lack of visibility of related tickets and manual intervention for routine requests like account creation.

IIA can be trained using historical ticket dump based on industry-standard machine learning algorithms (LogisticRegression, XGBoost, RandomForest, Multinominal NB) and can be integrated with ITSM tools to predict the various fields like assignment group, ticket category etc. in a ticket to help in routing the ticket. IIA auto assigns a support engineer to a ticket based on complexity & workload calculator, leave DB, SME mapping and shift roster.

# Key Features
- **Zero touch resolution:** IIA proposes resolutions to tickets based on historic data, KMDB, KEDB & pattern matching. IIA is integrated with Infosys Cognitive Automation Studio and brings in the capability to trigger a resolver bot from the Automation Studio. IIA also assist in auto ticket resolution with the help of scripts, automated SOPs, batch jobs etc.

- **Named Entity Recognition:** This ML based training capability of IIA extracts entities like server, service, username, user email etc. and their values from the ticket description and from the attached images in the tickets. It also allows users to add/modify the entities.
Image Analytics. IIA extends the training module to read and analyze screen images of application workflows. IIA can recommend the solution used in image training when an incident occurs with similar image in the attachment.

- **Delayed Prediction:** IIA enables cascaded prediction where a prior predicted field can be included in predicting the value for a next field.

- **Weighted whitelisting:** This feature improves the prediction accuracy by mapping the predicted value for a field to a set of key words tagged with certain weightage for each of them. These white listed key words derived from the domain/SME knowledge can be used to override the ML prediction value.

- **Explainable Assignment:** Explainable Assignment feature of IIA displays the matrix of calculated workload and availability details used in identifying the assignee for a ticket.

- **Always on Training:** IIA comes with a retraining feature. When retraining is going on system continues to use the old data for prediction and once the retraining is completed the old data can be replaced with the new data.

- **Related Ticket Search with 4 ML algorithms:** Text Rank, Word2Vec, Doc2Vec and BERT algorithms are included for the search functionality in finding the resolutions for the related ticket info/KMDB/Known errors pages. Users can choose the algorithm for search from the four algorithms.

- **Hinglish Support:** IIA is trained to identify whether the text in a ticket is in English or Hinglish. In case it identifies the text in Hinglish, flags the same to the user and request them to enter the details it in English.

# Prerequisite
- Python Version 3.9.7
- Mongodb Server Version 5
- Node.js Version 14.22
- Angular CLI Version 7.0.1 install using this command (npm install -g @angular/cli@7.0.1)
- Robo3T  Version 1.4


# Build Instructions
1.Download source code<br>
2.Extract the files to any path<br>
3.Create python environment, install all the dependencies using requirments.txt file with the help of IIA user manual present in the  Backend folder inside the source code.<br>
4.Restore **Db(mongodump.zip)** present in the Backend folder inside the source code.<br>
5.Run build_iia_frontend.bat present in the Infosys-Intelligent-Assistant inside the source code.<br>
6.Run run.bat present in the bin folder inside the source code.<br>
7.Open command prompt and set PYTHONPATH=src & python create_wheel_file.py to create IIA wheel file package for deployment. Package will get created inside dist folder upon succesful build.<br>

# Other Instructions
1.To know more about image analysis BPMN work flows refer [ScreenShotAnalysis_UsageGuide.pdf](https://github.com/Infosys/Infosys-Intelligent-Assistant/blob/main/Infosys-Intelligent-Assistant/readmeImages/ScreenShotAnalysis_UsageGuide.pdf)


# Introduction
<p align="center">
  <img src="https://github.com/Infosys/Infosys-Intelligent-Assistant/blob/main/Infosys-Intelligent-Assistant/readmeImages/one.png" width="800" class="center">
</p>


# Problem
<p align="center">
  <img src="https://github.com/Infosys/Infosys-Intelligent-Assistant/blob/main/Infosys-Intelligent-Assistant/readmeImages/two.png" width="800" class="center">
</p>


# Why IIA
<p align="center">
  <img src="https://github.com/Infosys/Infosys-Intelligent-Assistant/blob/main/Infosys-Intelligent-Assistant/readmeImages/three.png" width="800" class="center">
</p>


# Capabilities of IIA
<p align="center">
  <img src="https://github.com/Infosys/Infosys-Intelligent-Assistant/blob/main/Infosys-Intelligent-Assistant/readmeImages/four.png" width="800" class="center">
</p>


# Summary
<p align="center">
  <img src="https://github.com/Infosys/Infosys-Intelligent-Assistant/blob/main/Infosys-Intelligent-Assistant/readmeImages/five.png" width="800" class="center">
</p>

[InfosysIntelligentAssistant.ppt](https://github.com/Infosys/Infosys-Intelligent-Assistant/blob/main/Infosys-Intelligent-Assistant/readmeImages/IIA_Overview.pptx)
