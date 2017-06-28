# Pomulator是什么
Pomulator是一个基于Android模拟器的应用能耗、性能分析平台。
Pomulator是为了解决传统 Android 应用能耗分析的工具依赖于硬件支持，从而造成可扩 展性差、高成本、低效率的问题而设计的。有关Pomulator的具体实现细节可以参考《一种基于模拟器的移动应用能耗 分析平台的设计与实现》。


# Pomulator的环境搭建和运行方式
Pomulator修改了 Android系统底层的Linux Kernel和 Android模拟器实现了对能耗与性能事件的收集。

source目录中包含了，在Emulator层中和Kernel层中的修改patch，用户需要分别下载Android Emulator项目以及 Android Kernel项目，将patch分别打包到这连个项目中再进行编译和运行。

## Android Emulator项目的下载、应用patch、编译和运行

下载 studio项目，选择版本
```shell
mkdir studio-dev
cd studio-dev
repo init -u https://android.googlesource.com/platform/manifest -b studio-2.0
```

下载 编译所需的其他项目
```shell
cd studio-dev/external/qemu
android/scripts/build-mesa.sh
android/scripts/build-qemu-android.sh
```

 编译全部依赖
 ```shell
 cd studio-dev/external/qemu
 ./android-rebuild.sh
 ```
 
 应用patch
 ```shell
 cd studio-dev/external/qemu
 unzip qemu.zip
 
 cd studio-dev/external/qemu-android
 unzip qemu-android.zip
 ```
 
 运行模拟器,arm_ranchu_3_10_kernel_readfix可以替换为其他定制内核
 ```shell
 cd studio-dev/external/qemu
 ./objs/emulator -avd n5_7.0_arm_2 -kernel kernel_image/arm_ranchu_3_10_kernel_readfix -gpu on -show-kernel
 ```

 收集能耗信息
 ```shell
  cd studio-dev/external/qemu
  ./user_client_control
  输入s开启服务，输入1开始记录，输入0结束记录
 ```

## Android Kernel项目的下载、应用patch、编译和运行
