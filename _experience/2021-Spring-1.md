---
title: "Development of an OpenCV based vision inspection device"
collection: experience
type: "Workshop"
permalink: /experience/2021-Spring-1
#venue: "Huazhong University of Science and technology, School of Mechanical Science & Engineering"
date: 2021-03-15
location: "Wuhan, China"
excerpt: "Bottle cap testing machine <br/><img src='https://raw.githubusercontent.com/ShiMiaohui0426/ShiMiaohui0426.github.io/master/_experience/2021-Spring-1/SKLH.png'>"
---

# Preparing!!
# 基于OpenCV的视觉检测设备开发

项目信息：华中科技大学机械学院实验中心改造升级项目

直接负责人：黄弢

<center>
<img src='https://raw.githubusercontent.com/ShiMiaohui0426/ShiMiaohui0426.github.io/master/_experience/2021-Spring-1/SKLH.png'>
</center>
<center>
图1 视觉检测系统
</center>
本项目由华中科技大学机械学院国家级教学实验中心发起，黄弢老师负责。

- 项目时间：2021年12月-2021年03月
- 目标：
  1. 将这台机器改造成适合给本科生开课的展示机
  2. 开发检测产品用的代码（机器原有的代码不开源，不适合上课用）
  3. 重新设计这台机器的电气系统，使其与整个实验室的系统适配
- 最终结果：
    1. 基于OpenCV重新开发了瓶盖检测算法
    2. 使用Qt开发了该检测系统的人机交互界面
    3. 基于TwinCAT重新设计了电气系统
- 第三方合作单位：台州松科领航自动化有限公司

华中科技大学机械学院为了响应国家号召，对本学院的课程体系进行改革。为了满足智能制造中对于机器视觉及相关技术的需要，学院购买了一台被用于工业现场的视觉检测机。我被要求将这台机器改造成适合给本科生开课的展示机。在这个过程中，我负责了该机器的电气系统的重新设计，以及基于OpenCV的视觉检测算法的开发。

# 技术方案

该系统被分为上位机和下位机两部分。上位机主要负责与用户进行交互，图像的处理等，下位机负责采集传感器数据，触发相机拍照、控制光源等。其中，上位机由Qt开发，下位机由TwinCAT开发。
<center>
<img src='https://raw.githubusercontent.com/ShiMiaohui0426/ShiMiaohui0426.github.io/master/_experience/2021-Spring-1/System_Structure.jpg'>
</center>

<center>
图2 系统结构图
</center>

## 下位机

### TwinCAT

如上图所示，TwinCAT主要连接了相机、光源、光电传感器、电机等设备。在PLC程序中主要需要完成以下功能：

1. 根据光电传感器的信号变化，计算是否有瓶盖通过
2. 如果有瓶盖通过，则在传送皮带通过一定距离后触发相机拍照
3. 控制电机完成连续运动/点动/移动到特定位置等功能
4. 接收上位机的图像处理结果，控制气阀将不良品剔除
5. 根据一些硬件IO

### 环形数据结构设计

在PLC程序中，采用面向对象的设计思路，对于每一个瓶盖，都将其视为一个对象，代码如下：

```c
STRUCT
	ID:INT;
	InPostion:LREAL:=99999999;
	TestResult:BOOL;
END_STRUCT
END_TYPE
```

其中，ID是瓶盖的编号，InPostion是瓶盖进入传送带的位置，TestResult是瓶盖的检测结果。在PLC编程中，不允许动态分配内存，因此，需要在程序开始时就定义好数组的大小。为了方便，我将环形数组的大小定义为100。程序会不停的使用这个数组，因此，需要定义一个head和tail变量来记录数组的头尾位置。代码如下：

```c
VAR
	Queue: ARRAY [0..99] OF Product;
	head:INT:=0;
	tail:INT:=0;
	CameraOrder:INT:=0;//相机返回结果的位置
	CameraExeOrder:INT:=0;
	ElementNum:INT:=0;
END_VAR
```

该环形数组有另外分别实现了进入队列/出队列/获取队首/获取队尾等功能。在程序中，每当有瓶盖进入传送带时，就将其加入队列，每当有瓶盖离开传送带时，就将其从队列中移除。这样，就可以通过队列中的瓶盖对象来记录瓶盖的位置、检测结果等信息。
当接收到上位机发送的结果时，将其ID与队列中的瓶盖对象的ID进行比较，如果相同，则将该瓶盖对象的TestResult赋值为上位机发送的结果。当瓶盖通过剔除位时，如果该瓶盖对象的TestResult为TRUE（不良品），则将其从队列中移除。

### ADS通信
TwinCAT和上位机之间的通信采用ADS协议。在TwinCAT中，设计了两组数据结构分别用于上位机控制下位机的运行状态和接收图像处理的结果。分别为如下代码：

```c
STRUCT
	ctrlword :INT;
	stateword:INT;
	TarACSPos: ARRAY[0..11] OF LREAL;
	ActACSPos: ARRAY[0..11] OF LREAL;
END_STRUCT
END_TYPE
```

```c
STRUCT
	isValid:BOOL;
	ID:INT;
	Result:BOOL;
END_STRUCT
END_TYPE
```

根据ADS协议，TwinCAT会将这两组数据结构在内存中的地址发送给上位机，上位机通过这两个地址来读写数据。

## 上位机


上位机基于Qt和OpenCV开，以华中科技大学机械学院iCAT团队核心成员汪迪开发的RoboLab为基础，进行了二次开发。采用插件式的设计思路，将上位机分为多个模块，每个模块负责一个功能。在本项目中，主要包括以下模块：

1. 相机模块
2. 视觉处理模块
3. 通信模块

采用拖动式的操作模式，大大降低了学生学习算法时的挫败感。
<center>
<img src='https://raw.githubusercontent.com/ShiMiaohui0426/ShiMiaohui0426.github.io/master/_experience/2021-Spring-1/LeafVision.png'>
</center>
<center>
图3 我们研发的视觉软件
</center>

# 项目结果

最终，实验室的设备并未采用基于STM32芯片的采集卡方案。其原因是，PCB设计人员在设计时所设置的低频滤波器带来的信号失真过大。最终采用了北京某公司的成品采集卡。本人负责将其提供的程序接口集成封装为适合本科生上课使用的matlab函数。幸运的是，由本人编写的教学材料无需太多改动就可直接使用。

# 致谢

虽然最终这个设备没能被应用到项目中去，但在这期间学到的许多知识令我受益无穷。也非常感谢黄老师能在茫茫人海中选择我去进行这个项目的开发。也正是因为这个项目，我才有机会加入后续的更多项目。