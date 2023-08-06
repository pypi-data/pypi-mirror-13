# -*- coding: utf-8 -*-
import os
import time
from keywordgroup import KeywordGroup
from robot.api import logger
from selenium.webdriver.common.action_chains import ActionChains
try:
	import SendKeys
except ImportError:
	# try to import other lib for target OS platform
	pass
try:
	import win32gui
except ImportError:
	# try to import other lib for target OS platform
	pass

class _WebKeywords(KeywordGroup):

	# Public Web Keywords

	def web_hover_and_click(self, elementToHover_locator, elementToClick_locator):
		"""Hover and click

		(在运行该KW会将浏览器窗口移到你看不到的地方，以后也别想看到，屏幕截图是好的，哈哈~~)
		elementToHover_locator hover的区域位置，elementToClick_locator 要点击的元素位置
        | Web Hover And Click | ${elementToHover_locator} | ${elementToClick_locator} |
        | Web Hover And Click | locator1_hover | locator2_toclick |
		"""
		#self._current_browser().set_window_size(100, 100)#设置窗口大小
		self._current_browser().set_window_position(-10000, -10000)#设置窗口位置将窗口移出桌面。。。
		self._info("Hover '%s' and click '%s'" % (elementToHover_locator, elementToClick_locator))
		elementToHover = self._element_find(elementToHover_locator, True, False)
		elementToClick = self._element_find(elementToClick_locator, True, False)
		if elementToHover is None:
		    raise AssertionError("ERROR: Element %s not found." % (elementToHover_locator))
		if elementToClick is None:
			raise AssertionError("ERROR: Element %s not found." % (elementToClick_locator))
		actions = ActionChains(self._current_browser())
		actions.move_to_element(elementToHover)
		actions.click(elementToClick)
		actions.perform()
		self._current_browser().set_window_position(0, 0)#移回来了。。

	def web_upload_file(self, filepath):
		"""上传文件(用于flash上传控件)

		filepath 文件路径，支持绝对路径和相对路径，注意写法，例如：${CURDIR}${/}Res${/}Plus_Web${/}pic0.jpg
        ${CURDIR}指数据所在文件的当前路径
		RF中filepath的写法被认为是unicode
		另外，这里的输入依赖系统的输入法，建议提前切换至英文，用美式键盘最好
		| Web Upload File | ${filepath} |	
		| Web Upload File | ${CURDIR}${/}Res${/}Plus_Web${/}pic0.jpg | 	
		"""
		filepath=os.path.abspath(filepath)
		change = str(filepath)
		time.sleep(1)
		self._handle = win32gui.FindWindow(None, u"打开")#获取“打开”窗口的句柄
		win32gui.SetForegroundWindow(self._handle)#聚焦当前窗口
		SendKeys.SendKeys(change)
		time.sleep(1)
		SendKeys.SendKeys("{ENTER}")

	def web_open_browser(self, url):
		"""打开浏览器

		默认打开Chrome浏览器
		| Web Open Browser | ${url} |
		| Web Open Browser | http://www.163.com |
		"""		
		self.open_browser(url, 'chrome')

	def web_close_browser(self):
		"""关闭当前浏览器

		| Web Close Browser | |
		"""
		self.close_browser()		

	def web_click_element(self, locator):
		"""点击元素操作

		locator 同Selenium2Library里的locator
		| Web Click Element | ${locator} |
		| Web Click Element | id=username |
		"""		
		self.wait_until_page_contains_element(locator, 10)
		self.click_element(locator)	

	def web_click_text_button(self, text, selected_num=1):
		"""点击可以通过按钮内文字定位的Button

		text 为按钮内的文字
		如下的控件可以使用：<a href="/mass">群发消息</a>
		| Web Click Text Button | ${text} | ${selected_num} |
		| Web Click Text Button | 群发消息 | 2 |
		"""			
		common_locator = 'link=' + text	
		if self.web_get_elements_num(common_locator) > 0:
			self.web_click_chosen_element(common_locator, selected_num)	
		else:
			common_locator = "xpath=//*[text()='%s']" % text
			self.web_click_chosen_element(common_locator, selected_num)

	def web_input_text(self, locator, text, withenter='no'):
		"""向文本框中输入文本

		locator 同Selenium2Library里的locator
		text 用户名
		withenter 是否在最后按下Enter，默认是no
		| Web Input Text | ${locator} | ${text} |
		| Web Input Text | ${locator} | ${text} | ${withenter} |
		| Web Input Text | id=username | myaccount |
		| Web Input Text | id=username | myaccount | yes |
		"""
		self.wait_until_page_contains_element(locator, 10)
		self.input_text(locator, text)
		if withenter.lower() == 'yes':
			self.press_key(locator, '\\13')

	def web_input_password(self, locator, password):
		"""向文本框中输入密码

		locator 同Selenium2Library里的locator
		password 密码
		| Web Input Password | ${locator} | ${password} |
		| Web Input Password | id=password | mypassword |
		"""
		self.wait_until_page_contains_element(locator, 10)
		self.input_password(locator, password)

	def web_choose_file(self, locator, filepath):
		"""处理页面元素中input类型是file的元素，用来上传文件

		locator 同Selenium2Library里的locator
		filepath 文件路径，支持绝对路径和相对路径，注意写法
		| Web Choose File | ${locator} | ${filepath} |
		| Web Choose File | id=upload | ${CURDIR}${/}Res${/}Plus_Web${/}pic0.jpg |
		"""
		filepath=os.path.abspath(filepath)
		self.wait_until_page_contains_element(locator, 10)
		self.choose_file(locator, filepath)

	def web_select_frame(self, locator, selected_num=1):
		"""选locator定位的frame为当前的frame
		
		locator 同Selenium2Library里的locator
		selected_num 可以不填，默认是1，选取匹配的第一个元素
		| Web Select Frame | ${locator} | ${selected_num} |
		| Web Select Frame | name=iframe | 2 |
		"""
		selected_frame = self._get_selected_element(locator, selected_num)
		self._current_browser().switch_to_frame(selected_frame)

	def web_unselect_frame(self):
		"""设置顶层frame为当前frame

		| Web Unselect Frame | |
		"""
		self.unselect_frame()

	def web_click_chosen_element(self, locator, chosen_num=1):
		"""选择符合条件:locator定义的第chosen_num个元素，并点击它

		locator 元素定位
		chosen_num 符合的第chosen_num个元素，默认是1，选取匹配的第一个元素
		| Web Click Chosen Element | ${locator} | ${chosen_num} |
		| Web Click Chosen Element | id=myid | 2 |
		"""
		selected_element = self._get_selected_element(locator, chosen_num)
		selected_element.click()

	def web_confirm_alert_ok(self):
		"""对弹出的确认对话框选择OK

		| Web Confirm Alert Ok | |
		"""
		logger.info("点击Alert框确定按钮")
		self.confirm_action()

	def web_confirm_alert_cancel(self):
		"""对弹出的确认对话框选择取消

		| Web Confirm Alert Cancel| |
		"""
		logger.info("点击Alert框取消按钮")
		self.choose_cancel_on_next_confirmation()#设置_cancel_on_next_confirmation为True
		self.confirm_action()

	def web_page_screenshot(self, filename=None):
		"""截屏

		filename 自定义文件名
		| Web Page Screenshot | ${filename} |
		| Web Page Screenshot |  |
		| Web Page Screenshot | pic1 |
		"""
		self.capture_page_screenshot(filename)

	def web_select_from_list(self, locator, *value):
		"""选择下拉框

		locator 元素位置
		value 下拉框中的对应值
		| Web Select From List | ${locator} | ${value} |
		"""
		self.wait_until_page_contains_element(locator, 10)
		self.select_from_list(locator, *value)
		

	def web_get_text(self, locator):
		"""获取locator位置的text对应值

		locator 同Selenium2Library里的locator
		| Web Get Text | ${locator} |
		| Web Get Text | id=myid |
		"""
		self.wait_until_page_contains_element(locator, 10)
		return self.get_text(locator)

	def web_get_title(self):
		"""获取当前页面的标题

		| Web Get Title | |
		"""
		return self.get_title()

	def web_maximize_browser_window(self):
		"""最大化浏览器窗口

		| Web Maximize Browser Window | |
		"""
		self.maximize_browser_window()

	def web_go_to(self, url):
		"""跳转到提供的url

		| Web Go To | ${url} |
		| Web Go To | http://www.163.com |
		"""	
		self.go_to(url)

	def web_page_should_contain(self, text):
		"""验证当前页面是否包含text

		text 页面包含的文本
		| Web Page Should Contain | ${text} |
		| Web Page Should Contain | Hello! |
		"""
		self.wait_until_page_contains(text, 10)
		self.page_should_contain(text)

	def web_page_should_not_contain(self, text):
		"""验证当前页面是否包含text

		text 页面不包含的文本
		| Web Page Should Not Contain | ${text} |
		| Web Page Should Not Contain | Hello! |
		"""
		self.wait_until_page_does_not_contain(text, 10)
		self.page_should_not_contain(text)
	
	def web_page_should_contain_element(self, locator):
		"""验证当前页面是否包含locator定位的元素

		locator 元素定位
		| Web Page Should Contain Element | ${locator} |
		| Web Page Should Contain Element | id=myid |
		""" 
		self.wait_until_page_contains_element(locator, 10)
		self.page_should_contain_element(locator)

	def web_page_should_not_contain_element(self, locator):
		"""验证当前页面是否包含locator定位的元素

		locator 元素定位
		| Web Page Should Not Contain Element | ${locator} |
		| Web Page Should Not Contain Element | id=myid |
		""" 
		self.wait_until_page_does_not_contain_element(locator, 10)
		self.page_should_not_contain_element(locator)

	def web_execute_javascript(self, *code):
		"""执行javascript代码

		代码可能错误，需要修改
		| Web Execute Javascript | ${*code} |
		| Web Execute Javascript | window.document.getElementById('foo') |
		"""
		return self.execute_javascript(*code)	

	def web_get_alert_message(self):
		"""返回当前JavaScript alert的text

		| Web Get Alert Message | |
		"""
		return self.get_alert_message()

	def web_select_window(self, locator=None):
		"""选择窗口

		请结合Web Get Title使用
		| Web Select Window | ${locator} |
		| *Strategy* | *Example*                               | *Description*                        |
        | title      | Select Window `|` title=My Document     | Matches by window title              |
        | name       | Select Window `|` name=${name}          | Matches by window javascript name    |
        | url        | Select Window `|` url=http://google.com | Matches by window's current URL      | 
		"""
		self.select_window(locator)	

	# 后添加KW，可用性不强
	def web_get_elements_num(self, locator):
		"""返回符合locator定义的元素的个数 0-n

		| Web Get Elements Num | ${locator} |
		| Web Get Elements Num | id=myid |
		"""		
		try:
			self.wait_until_page_contains_element(locator, 10)
			elements_list = self.get_webelements(locator)
		except Exception:
			#raise AssertionError("ERROR: Element %s not found." % (locator))
			return 0		
		return len(elements_list)

	def web_get_element_isDisplayed(self, locator):
		"""返回locator定位的元素是否可见，返回True或者false

		| Web Get Element IsDisplayed | ${locator} |
		| Web Get Element IsDisplayed | xpath=//div[@class='edit-btn'] |
		"""
		element = self._element_find(locator, True, False)
		return element.is_displayed()

	def _get_selected_element(self, locator, selected_num=1):
		"""返回选中的元素

		locator 元素位置
		selected_num 元素序号，从1开始
		"""
		self.wait_until_page_contains_element(locator, 10)
		index = int(selected_num) - 1
		elements_list = self.get_webelements(locator)
		if index < len(elements_list):
			return elements_list[index]
		else:			
			raise AssertionError("ERROR: Element selected_num %d is out of the length of elements_list" % int(selected_num))