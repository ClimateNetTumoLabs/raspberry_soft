python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

deactivate
cd venv/lib/python3.10/site-packages
zip -r9 ${OLDPWD}/lambda_function.zip .
cd $OLDPWD
zip -g lambda_function.zip lambda_function.py
zip -g lambda_function.zip config.py
