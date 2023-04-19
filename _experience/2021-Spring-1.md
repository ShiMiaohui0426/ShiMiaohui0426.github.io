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

### AD7606

AD7606除了与STM32f4通过SPI连接之外，另外还有一个触发脚用于接收PWM信号，在PWM的每个上升沿触发采集。

### 双缓冲设计

在该系统中，为了能够最大程度上将设备的性能利用起来，并且保证采集到的数据的连续性，在发送数据时，需要使用到双缓冲的设计方法。

首先定义需要使用到的缓冲数组

```c
#define TX_BUF_LEN_USB 1024*16
uint8_t txBuf_usb[2][TX_BUF_LEN_USB];
```

在读取到数据后，将数据填写入缓冲区。

```c
AD7606_Read8CH();	
		if(AD_CH_ctrl & AD_CH1){
	#ifdef AD_CH1
	txBuf_usb[ctrl_word][txCount_usb++]=AD7606_BUF.shortbuf[0];
	txBuf_usb[ctrl_word][txCount_usb++]=AD7606_BUF.shortbuf[1];
	#endif
	}
//... 
//...
//...
	if(AD_CH_ctrl & AD_CH8){
	#ifdef AD_CH8
	txBuf_usb[ctrl_word][txCount_usb++]=AD7606_BUF.bytebuf[14];
	txBuf_usb[ctrl_word][txCount_usb++]=AD7606_BUF.bytebuf[15];	
	#endif
	}
```

在发送函数中，实现缓冲区的交换

```c
void AD7606_USB_Send(void){
	if(txCount_usb >= TX_BUF_LEN_USB)
	{ ctrl_word = !ctrl_word;
		txCount_usb = 0;
		UsbSendData(txBuf_usb[ctrl_word],TX_BUF_LEN_USB);//USB发送
		LED_Toggle();
	}
};
```

### 时钟同步

本系统中共有两个时钟被使用。时钟1是用于生成固定频率的PWM波用于触发采集。时钟2是用于驱动SPI读取采集结果。根据AD7606的官方手册，选择了在转换期间读取的方法。
<center>
<img src='https://raw.githubusercontent.com/ShiMiaohui0426/ShiMiaohui0426.github.io/master/_experience/2019-Fall-1/Untitled%201.png'>

</center>
<center>
图3 AD7606采样时读取-时序图
</center>
在SPI读取数据时，触发其执行的时钟并不能继续计时，如果不做处理的话，每次的读取时间都会延后。举个例子，第一次读取的时候，采集和读取在同一时间进行。到了第二次，读取的时间就会向后延迟t秒，t代表读取所花费的时间。当达到某个值后，就会丢掉一个数据。为了避免这种情况，我们在每次读取结束之后，将时钟2的计数器设置为时钟1的值，这样就能保证采集和读取总是同步触发了。

```c
TIM2->ARR=TIM1->ARR;
```

## 上位机

上位机需要通过USB来与下位机通信，但是由于Matlab的性能限制，如果将得到的原始数据放在Matlab中处理的话，将会十分耗时。于是使用了Mex混合编程的方法，使用C++与下位机通信，并将其封装成Matlab函数。编译得到的mexw64文件可以很方便的部署到各个设备上。

### Matlab
对于接受这个课程的学生来说，他们中的大多数都是首次接触到Matlab编程。于是作为课程开发者，我的另一项任务就是为他们提供例程与教程。
<center>
<img src='https://raw.githubusercontent.com/ShiMiaohui0426/ShiMiaohui0426.github.io/master/_experience/2019-Fall-1/matlab.png'>
</center>
<center>
图4 Matlab AppDesigner的例程
</center>

除了有关AppDesigner的教程之外，仍需要为参加这门课的学生提供采集卡的调用例程。

``` MATLAB

state=USBDAQ_opencard();%打开采集卡
Fs=5000;
N=1000;
CH_on=zeros(1,8);
CH_on(8)=1;
CH_on(1)=1;
%这时通道控制字为1010 0000，通道号由高位向低位排布，八通道由第一位控制，七通道由第二位控制，以此类推
%传递参数时，需要将二进制的数转换成十进制的数
%未被使能的通道将会回传一堆0
CHcode=CH_on(8)*128+CH_on(7)*64+CH_on(6)*32+CH_on(5)*16+CH_on(4)*8+CH_on(3)*4+CH_on(2)*2+CH_on(1);
data=USBDAQ_readdata(N,Fs,CHcode);%该函数返回N*8的2维数组
CH1data=data(:,1);%获取通道1数据
CH2data=data(:,2);%获取通道2数据
CH3data=data(:,3);%获取通道3数据
CH4data=data(:,4);%获取通道4数据
CH5data=data(:,5);%获取通道5数据
CH6data=data(:,6);%获取通道6数据
CH7data=data(:,7);%获取通道7数据
CH8data=data(:,8);%获取通道8数据
USBDAQ_closecard();%关闭采集卡

```

# 项目结果

最终，实验室的设备并未采用基于STM32芯片的采集卡方案。其原因是，PCB设计人员在设计时所设置的低频滤波器带来的信号失真过大。最终采用了北京某公司的成品采集卡。本人负责将其提供的程序接口集成封装为适合本科生上课使用的matlab函数。幸运的是，由本人编写的教学材料无需太多改动就可直接使用。

# 致谢

虽然最终这个设备没能被应用到项目中去，但在这期间学到的许多知识令我受益无穷。也非常感谢黄老师能在茫茫人海中选择我去进行这个项目的开发。也正是因为这个项目，我才有机会加入后续的更多项目。