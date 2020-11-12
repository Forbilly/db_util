# db_util -  懒加载封装数据库工具

### 基于Django的懒加载思想

### 内部实现一个灵活的数据库使用方法

#### 外部调用使用懒加载方式进行封装

##### 目前实现数据库： mongodb， mysql，db_postgre

##### 队列方式： Rabitmq

##### 初始化懒加载配置文件信息：setting

```
优势： 调用时加载, 节省内存空间
       数据库操作多线程安全, 类mongodb语法查询
       简单灵活，无需加载模型类对象
```

![懒加载数据库封装](https://github.com/Forbilly/db_util/blob/main/%E6%87%92%E5%8A%A0%E8%BD%BD%E6%95%B0%E6%8D%AE%E5%BA%93%E5%B0%81%E8%A3%85.png)
