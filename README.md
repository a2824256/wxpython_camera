# wxpython_camera
wxpython编写的获取摄像头图像程序，支持一般免驱摄像头、zed mini、intel realsense

# 已测试的摄像头类型
[x]640 x 480分辨率的免驱摄像头
[x]intel realsense双目摄像头
[x]zed mini双目摄像头

# 使用方法
点击take photo按钮

# Conda环境配置（python 3.7）
安装wxpython
```shell
conda install wxpython
```
安装opencv
```
conda install -c menpo opencv
``` 
安装zed mini驱动<br>
教程:https://github.com/stereolabs/zed-python-api/blob/master/README.md

安装intel realsense驱动(Mac需要手动编译源码安装)
```shell
pip install pyrealsense2
```
# Update history
##### 2020/03/07
1. 支持普通免驱摄像头

##### 2020/04/26
1. 支持zed mini摄像头


# TODO List
1.更新使用教程<br>
2.完善摄像头类型选择逻辑
