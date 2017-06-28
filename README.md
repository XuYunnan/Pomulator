# Pomulator是什么
Pomulator是一个基于Android模拟器的应用能耗、性能分析平台。
Pomulator是为了解决传统 Android 应用能耗分析的工具依赖于硬件支持，从而造成可扩 展性差、高成本、低效率的问题而设计的。有关Pomulator的具体实现细节可以参考《一种基于模拟器的移动应用能耗 分析平台的设计与实现》。


# Pomulator的环境搭建和运行方式
Pomulator修改了 Android系统底层的Linux Kernel和 Android模拟器实现了对能耗与性能事件的收集。

source目录中包含了，在Emulator层中和Kernel层中的修改patch，用户需要分别下载Android Emulator项目以及 Android Kernel项目，将patch分别打包到这连个项目中再进行编译和运行。

## Android Emulator项目的下载、应用patch、编译和运行

## Android Kernel项目的下载、应用patch、编译和运行
