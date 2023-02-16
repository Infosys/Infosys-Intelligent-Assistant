# intent-python
Below are the new packages that needs to be installed to run the latest modularized code
1.	NLTK

        1.	Go to start type env, select ‘edit environment variables for your account’.

        2.	Create two new environment variable as http_proxy, https_proxy with value as
        
            http_proxy = http://user_name:password@10.74.91.103:80/
            https_proxy = http://user_name:password@10.74.91.103:80/
            For the password in this variable, if your password has any special character then replace it with its equivalent hex code, for example replace ‘!’ with %21, ‘@’ with %40
            Etc.
            Example:- http_proxy =  http://akshay.kalra:123%21456@10.74.91.103:80/

        3.	After creating an environment variable, restart your system.
        
        4.	Now go to python interpreter and write this two lines of code:-
            a.	Import nltk
            b.	Nltk.download(‘all’)
            
2.	TEXTBLOB

    a.	Open Anaconda prompt as admin and type “conda install -c conda-forge textblob”.

3.	APSCHEDULER

    a.	“conda install -c conda-forge textblob”.

4.	Flask-restful

    a.	conda install -c anaconda flask-restful
    
5.	flask

    a.	conda install -c anaconda flask
    
6.	xgboost

    a.	conda install -c conda-forge xgboost
    
7.	pysnow & servicenow

    a.	Open cmd as admin
    
    b.	Type set HTTP_PROXY=
    
    c.	Type Set HTTPS_PROXY=
    
    d.	Type “pip install <packagename> -i http://infynp.ad.infosys.com/repository/pypi-all/simple --trusted-host infynp.ad.infosys.com”. Then it will ask for your username and password.
    
    Example : pip install pysnow -i http://infynp.ad.infosys.com/repository/pypi-all/simple --trusted-host infynp.ad.infosys.com
    
Note:- If you are not able to install any of the packages from 2-6 then try the steps used to get pysnow and servicenow (7). 


************************* Removed name *************************
In run_scheduler_predict.py payload needs admin username and password.
In intent.ini path required for ebin & kb_knowledge template.xlsx and exception_url if any
In provideaccesstoIIA.py give email_id to user_mailid variable
In provideaccesstoIIA.py give email_id to user_mailid variable
In recommendationmodel.py give used id and password for office365url
In \src\intent\customITSM\LTFS_ManageEngine_Configurations.py provide proxies dict in this format (https':'https:// username:password@ipaddress/ 
In \src\intent\resolution\resolution.py provide username and password in body variable.
In \src\intent\resolution\resolution.py replace UI_PATH_URL to actual UI path orchestrator url.
In \src\intent\resolution\resolution.py give 'icas_url' in config.ini.