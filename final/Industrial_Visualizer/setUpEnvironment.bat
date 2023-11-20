set ENV_NAME=CS437

CALL conda create --name %ENV_NAME% python=3.11

CALL conda install -n %ENV_NAME% numpy
CALL conda install -n %ENV_NAME% pyqt
CALL conda install -n %ENV_NAME% pyserial
CALL conda install -n %ENV_NAME% pyopengl
CALL conda install -n %ENV_NAME% pyqtgraph==0.11.0
CALL conda install -n %ENV_NAME% scipy
CALL conda install -n %ENV_NAME% matplotlib
CALL conda install -n %ENV_NAME% pyserial
CALL conda install -n %ENV_NAME% jupyter notebook