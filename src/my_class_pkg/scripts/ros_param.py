#!/usr/bin/env python3
import rospy

def param_demo():
    rospy.init_node("param_demo")
    rate = rospy.Rate(1)  # 1Hz循环
    while(not rospy.is_shutdown()):
        # 1. 获取参数，无参数则使用默认值
        parameter1 = rospy.get_param("param1", default=111)
        parameter2 = rospy.get_param("param2", default=222)
        rospy.loginfo('Get param1 = %d', parameter1)
        rospy.loginfo('Get param2 = %d', parameter2)

        # 2. 设置参数
        rospy.set_param('param2', 2)

        # 3. 删除参数
        rospy.delete_param('param2')

        # 4. 检查参数是否存在
        ifparam3 = rospy.has_param('param3')
        if(ifparam3):
            rospy.loginfo('param3 exists')
        else:
            rospy.loginfo('param3 does not exist')

        # 5. 获取所有参数名称
        params = rospy.get_param_names()
        rospy.loginfo('param list: %s', params)

        rate.sleep()

if __name__=="__main__":
    try:
        param_demo()
    except rospy.ROSInterruptException:
        pass

