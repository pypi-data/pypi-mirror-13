# -*- coding: utf-8 -*-
import sys
from keywordgroup import KeywordGroup
from time import sleep

#默认设备屏幕参数
DEFAULT_HEIGHT=1920
DEFAULT_WIDTH=1080
#屏幕密度
DEFAULT_DENSITY=480.0
#起始坐标，L_PX_X是用屏幕宽减去X坐标
L_PX_X=1080-900
PX_Y=170
#像素间距（单元格）
PX_PITCH=150

class _MobileKeywords(KeywordGroup):
    """
    _MobileKeywords including the Wrapper Keywords for RFUI Framework specially. 
    Move from the common_lib_mobile.py.
    The following keywords can be add/delete/modify according to the RFUI Framework requirement.
    """
    def __init__(self):
        self._desired_caps = None
        #dip为单位的坐标起点，单元格间距，设置右上角为坐标远点
        self._start_x = L_PX_X / DEFAULT_DENSITY
        self._start_y = PX_Y / DEFAULT_DENSITY 
        self._px_picth = PX_PITCH / DEFAULT_DENSITY

    # Public, keywords
    def Mobile_Open_Application(self, myremote_url, myalias=None,  **kwargs):
        """打开Moible(IOS/Android)端APP
        | Mobile_Open_Application | ${remote_url} | MyIOSapp | platformName=iOS | platformVersion=9.1 | deviceName='iPhone 6' app=${yourapp_path} | 
        """   
        self._desired_caps = kwargs    
        myindex = self.open_application(myremote_url, alias=myalias, **kwargs)
        print "index of open_application: %s" % myindex
        return myindex

    def Mobile_Close_Application(self):
        """关闭 当前活动的Moible(IOS/Android)端APP
        | Mobile_Close_Application | 
        """       
        self.close_application()
        print "close_application!"

    def Mobile_Switch_Application(self, alias_or_index):
        """切换至指定的alias_or_index Moible(IOS/Android)端APP
        | Mobile_Switch_Application | ${alias_or_index} |
        | Mobile_Switch_Application | MyIOSapp |
        """
        self.switch_application(alias_or_index)
        print "switch_application to alias_or_index:" + alias_or_index
        print alias_or_index

    def Mobile_Click_Element(self, locator, target_num=1):
        """点击locator定义的元素， （locator搜索结果为多个元素，默认点击其中第一个，可以设定target_num，点击指定第n元素）
        locator: 同AppiumLibrary里的locator;
        target_num: 指定元素序号.
        [不输入（默认值）:   点击第一个元素]
        [=0 :                点击最后一个元素]
        [=x（>0）:           点击第x个元素]

        | Mobile_Click_Element | ${locator} |
        Android Native: 
        | Mobile_Click_Element | identifier=myid |
        | Mobile_Click_Element | xpath=//android.widget.TextView[@text="文本"] |
        | Mobile_Click_Element | xpath=//android.widget.lsView/android.widget.RelativeLayout[3] |
        @text表示的是android.widget.TextView的一个text属性，"文本"是该属性的值，用""引起来，是xpath的一种写法
        
        Android WebView: 
        | Mobile_Click_Element | accessibility_id=公众号名称 |
        | Mobile_Click_Element | accessibility_id=公众号名称 | 0 |
        
        IOS Native: 
        | Mobile_Click_Element | identifier=myid |
        | Mobile_Click_Element | id=public icon normal |
        | Mobile_Click_Element | xpath=//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIATextField[2] |

        IOS WebView:
        | Mobile_Click_Element | xpath=//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIAWebView[1]/UIAStaticText[27] |

        locator 示例:
        | identifier Click Element | identifier=my_element | Matches by @id or @name attribute |
        | id Click Element | id=my_element | Matches by @id attribute |
        | name Click Element | name=my_element | Matches by @name attribute |
        | xpath Click Element | xpath=//UIATableView/UIATableCell/UIAButton | Matches with arbitrary XPath | 
        | class Click Element | class=UIAPickerWheel | Matches by class | 
        | accessibility_id Click Element | accessibility_id=t | Accessibility options utilize. | 
        """
        self.wait_until_page_contains_element(locator, timeout=20, error=u"等待元素加载失败")

        #Click the only one or first one
        if target_num==1:
            self.click_element(locator)
        #Click the target one( 2nd,3rd,...,last(0))
        else:
            index = int(target_num) - 1
            elements_ls = self.get_elements(locator)
            if index <= len(elements_ls):
                elements_ls[index].click()
            else:
                self.capture_page_screenshot() 
                #print "The target_num is out of the length of elements_ls, Please double check."
                raise AssertionError("The target_num is '%s', which is out of the length of elements_ls searched by '%s'." % (target_num, locator))

    def Mobile_Click_Text_Button(self, text, target_num=1):
        """点击可以通过按钮内文字定位的Button， （相同文字的按钮如果是多个，默认点击其中第一个，可以设定target_num，点击指定第n元素）
        text: 为按钮内的文字, 比如： 欢迎页－登录  主菜单页－发现／好友／电话／我
        target_num: 指定元素序号
        [不输入（默认值）:   点击第一个元素]
        [=0 :                点击最后一个元素]
        [=x（>0）:           点击第x个元素]
        
        | Mobile_Click_Text_Button | ${text} |
        IOS/Android:
        | Mobile_Click_Text_Button | 登录 |
        | Mobile_Click_Text_Button | ${text} |
        | Mobile_Click_Text_Button | 发送的消息内容 | 0 |
        | Mobile_Click_Text_Button | 发送的消息内容 | 3 |
        """
        _platform = self._desired_caps['platformName']

        if _platform.lower() == 'android':
            #Android example:   xpath=//*[@text=“登录”]
            mylocator = 'xpath=//*[@text=' + '"' + text + '"]'
            #mylocator = 'xpath=//android.widget.Button[@text=' + '"' + text + '"]'
        else:
            #iOS example: id=登录 
            mylocator = 'identifier=' + text
            #mylocator = 'id=' + text

        self.Mobile_Click_Element(mylocator, target_num)

    def Mobile_Long_Press(self, locator):
        """长时间按 locator定义的UI元素
        locator: 同AppiumLibrary里的locator
        | Mobile_Long_Press | ${locator} |
        """
        self.wait_until_page_contains_element(locator, timeout=10, error=u"等待元素加载失败")
        self.long_press(locator)

    def Mobile_Long_Press_Text_Button(self, text):
        """长时间按 可以通过按钮内文字定位的Button
        text: 为按钮内的文字
        | Mobile_Long_Press_Text_Button | ${text} |
        | Mobile_Long_Press_Text_Button | 发送的消息 |
        """
        _platform = self._desired_caps['platformName']
        if _platform.lower() == 'android':
            #Android example:   xpath=//*[@text=“登录”]
            mylocator = 'xpath=//*[@text=' + '"' + text + '"]'
        else:
            #iOS example: id=登录 
            mylocator = 'identifier=' + text
        self.Mobile_Long_Press(mylocator)

    def Mobile_Input_Text(self, locator, text):
        """向文本框中输入文本
        | Mobile_Input_Text | ${locator} |  ${text} |
        locator: 同AppiumLibrary里的locator
        text: 用户名
        """
        self.wait_until_page_contains_element(locator, timeout=10, error=u"等待元素加载失败")
        self.input_text(locator, text)

    def Mobile_Clear_Text(self, locator):
        """清空文本框中的文本
        | Mobile_Clear_Text | ${locator} |
        locator: 同AppiumLibrary里的locator
        """
        self.wait_until_page_contains_element(locator, timeout=10, error=u"等待元素加载失败")
        self.clear_text(locator)

    def Mobile_Capture_Page_Screenshot(self):
        """抓取当前页面截屏图片
        | Mobile_Capture_Page_Screenshot |
        """
        self.capture_page_screenshot() 

    def Mobile_Page_Should_Contain_Text(self, text):
        """验证当前页面是否包含text, 即使判断成功 log也抓图留证.
        | Mobile_Page_Should_Contain_Text | ${text} |
        """
        self.wait_until_page_contains(text, timeout=10)
        self.page_should_contain_text(text)
        #self.capture_page_screenshot()    #capture the page evenif the kw pass.

    def Mobile_Page_Should_Contain_Element(self, locator):
        """验证当前页面是否包含locator定位的元素, 即使判断成功 log也抓图留证.
        | Mobile_Page_Should_Contain_Element | ${locator} |
        """
        self.wait_until_page_contains_element(locator, timeout=10)
        self.page_should_contain_element(locator)
        self.capture_page_screenshot()    #capture the page evenif the kw pass.

    def Mobile_Page_Should_Not_Contain_Text(self, text):
        """验证当前页面是否 不包含text, 即使判断成功 log也抓图留证.
        | Mobile_Page_Should_Not_Contain_Text | ${text} |
        """
        self.wait_until_page_does_not_contain(text, timeout=10)
        self.page_should_not_contain_text(text)
        self.capture_page_screenshot()    #capture the page evenif the kw pass.

    def Mobile_Page_Should_Not_Contain_Element(self, locator):
        """验证当前页面是否 不包含locator定位的元素, 即使判断成功 log也抓图留证.
        | Mobile_Page_Should_Not_Contain_Element | ${locator} |
        """
        self.wait_until_page_does_not_contain_element(locator, timeout=10)
        self.page_should_not_contain_element(locator)
        self.capture_page_screenshot()    #capture the page evenif the kw pass.

    def Mobile_Swipe(self, start_x, start_y, end_x, end_y, duration=1000):
        """定义滑动操作

        添加了1s延迟
        start_x 起始x轴坐标
        start_y 起始y轴坐标
        end_x 结束x轴坐标
        end_y 结束y轴坐标
        duration 操作的时间间隔单位ms
        | Mobile_Swipe | start_x | start_y | end_x | end_y | duration |
        """
        sleep(1)#延迟1s
        self.swipe(start_x, start_y, end_x, end_y, duration)

    def Mobile_Get_Element_Attribute(self, locator, attribute):
        """获取指定位置元素的属性

        locator 元素位置
        attribute 属性：name, value, text...
        | Mobile Get Element Attribute | locator | name |
        | Mobile Get Element Attribute | locator | text |
        """
        self.wait_until_page_contains_element(locator)
        return self.get_element_attribute(locator, attribute)

    def Mobile_Set_Device_Info(self, args):
        """Android设置设备信息，用于坐标点击

        可以传入3个参数，以英文逗号隔开，顺序依次如下
        width 设备屏幕宽度
        height 设备屏幕高度        
        density 设备屏幕像素密度
        | Mobile Set Device Info | ${width,height,density} |
        | Mobile Set Device Info | 1080,1920,480 |
        查询设备以上信息
        $ adb shell wm
        usage: wm [subcommand][options]
        wm size [reset|WxH]
        wm density [reset|DENSITY]
        wm overscan [reset|LEFT,TOP,RIGHT,BOTTOM]
        """
        ls = args.split(',')
        d = float(ls[2])
        self._width = float(ls[0])
        self.start_x = self._start_x * d
        self.start_y = self._start_y * d
        self.px_picth = self._px_picth * d
     
    def Mobile_Choose_Item(self, num):
        """选择第几个Item，用于Android暂时不能获取的PopupWindow

        使用前需先调用Mobile Set Device Info设置设备信息
        num 第num个Item
        | Mobile Choose Item | num |
        | Mobile Choose Item | 2 |
        """
        n = int(num)
        x = self._width - self.start_x
        y = self.start_y + (n - 1) * self.px_picth
        self.click_a_point(x, y)  

    def Mobile_Click_WebView_TextElement(self, text, target_num=1):
        """用于Android端WebView中的带文本的元素点击操作,支持自动滚屏，可以点击未进入webview屏幕的元素

        | Mobile_Click_WebView_TextElement | 更多游戏 | 
        如果有重复元素，可以用target_num选择第几个
        | Mobile_Click_WebView_TextElement | ${text} | ${target_num}|
        | Mobile_Click_WebView_TextElement | 下载 | 3 |
        """
        textelement = 'accessibility_id=' + text
        #try search elment with ${text}, if failed try search element with ${text}+' Link' (易信内置webview)
        try:
             self.wait_until_page_contains_element(textelement, timeout=10, error=u"等待元素加载失败")
        except Exception:
             textelement += " Link" 
        #finally:
             #print textelement        
        #self.Mobile_Click_Element(textelement, target_num) 
        self.Mobile_Click_WebView_Element(textelement, target_num)

    def Mobile_Click_WebView_Element(self, locator, target_num=1):
        """用于Android端WebView中locator定义的元素点击操作,支持自动滚屏，可以点击未进入webview屏幕的元素

        | Mobile_Click_WebView_Element | accessibility_id=webview_ico_home_games_all_played_2x |
        如果有重复元素，可以用target_num选择第几个
        | Mobile_Click_WebView_Element | ${text}  | 3 |
        """
        self.wait_until_page_contains_element(locator, timeout=10, error=u"等待元素加载失败")
        self._click_webview_element_autoswipe(locator, target_num)

# Private 

   # swipe loop + element.click,  game platform and normal webview
    def _click_webview_element_autoswipe(self, target_locator, target_num=1):
        #get webview location+size
        webview_element = self.get_elements('class=android.webkit.WebView', True)
        webview_location = webview_element.location.values()
        webview_size = webview_element.size.values()

        #get element location+size
        if target_num==1:
            target_element = self.get_elements(target_locator, True)
        else:
            index = int(target_num) - 1
            elements_ls = self.get_elements(target_locator)
            if index <= len(elements_ls):
                 target_element = elements_ls[index]
            else:
                self.capture_page_screenshot() 
                #print "The target_num is out of the length of elements_ls, Please double check."
                raise AssertionError("The target_num is '%s', which is out of the length of elements_ls searched by '%s'." % (target_num, target_locator))
        des_loc = target_element.location.values()
        des_size = target_element.size.values()

        des_size_width = des_size[0]
        des_size_height = des_size[1]
        des_loc_y = des_loc[0]
        des_loc_bottom = des_loc_y + des_size_height
        des_loc_x = des_loc[1]
        webview_y = webview_location[0]
        webview_height = webview_size[1]
        webview_bottom = webview_y + webview_height
        print 'webview_location: (%d, %d)'%(webview_location[1], webview_y)
        print 'webview_size: (%d, %d)' % (webview_size[0], webview_height)
        print 'des_loc: (%d, %d)' % (des_loc_y, des_loc_x)
        print 'des_size: (%d, %d)' % (des_size_width, des_size_height)

        start_loc_y = webview_y
        start_loc_x = des_loc_x + int(des_size_width/2)

        swipe_distance = webview_height-1
        swipe_times = (des_loc_bottom - webview_bottom)/webview_height + 2
        #swipe the webview, get new element location, click the element if it's present in screen(des_loc_y<webview_bottom)
        while (swipe_times > 0):
            print '[debug] swipe_times : %d' % swipe_times
            swipe_times -=1
            if target_num==1:
                target_element = self.get_elements(target_locator, True)
            else:
                index = int(target_num) - 1
                elements_ls = self.get_elements(target_locator)
                target_element = elements_ls[index]

            des_loc = target_element.location.values()
            des_size = target_element.size.values()
            des_loc_y = des_loc[0] + des_size[1]

            print '[debug] Swipe Loop: New des_loc_y: %d, While webview_bottom: %d' % (des_loc_y, webview_bottom)
            if ( des_loc_y <= webview_bottom ):
                target_element.click()
                print '[debug] Click the elment by element.click with locator: %s' % target_locator
                break
            
            print '[debug] Do swipe with swipe_distance: %d' % swipe_distance
            self.swipe(start_loc_x, start_loc_y+swipe_distance, start_loc_x, start_loc_y, 3000)
            #self.swipe(start_loc_x, start_loc_y, start_loc_x-30, start_loc_y, 1000) 
            sleep(2)
