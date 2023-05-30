# _*_ coding:UTF-8 _*_  
import os
import sys
import traceback
import json
import time
import re
import win32gui  
import win32api
import win32con
from ctypes import windll
from optparse import OptionParser

from lib.helper.xmlparse import APPOpsXml
from lib.winutil.utils import ProcUtil,WinUtil,MouseUtil,CursorUtil,MsgUtil

reload(sys) 
sys.setdefaultencoding('utf8')

def get_realpath():
    return os.path.split(os.path.realpath(__file__))[0]

def get_binname():
    return os.path.split(os.path.realpath(__file__))[1]

def get_right_content(content):
    try:
        content = content.decode("utf8")
    except Exception:
        try:
            content = content.decode("gbk")
        except Exception:
            try:
                content = content.decode("GB2312")
            except Exception:
                pass
    return content
    
def actions(action_steps):
    try:
        hwds = []
        id_whds = {}
        for idx,action_conf in enumerate(action_steps):
            action = action_conf.get("action", "")
            data = action_conf.get("data", {})
            func = action_conf.get("func", "")
            func = get_right_content(func)
            
            print u"[STEP-%s]" % (idx+1)
            print u"Action: %s" % (action)
            print u"Func: %s" % (func)
            print u"Config: %s" % (json.dumps(data, encoding="UTF-8", ensure_ascii=False))
            
            ## GUI程序
            if action == "run":
                binpath = data.get("binpath", "")
                params = data.get("params", "")
                wid = data.get("id", None)
                if not wid:
                    print "[Warn] Do Not Assign ID."
                params = params if params else ""
                bps = re.split(";", binpath)
                avail_bp = None
                for bp in bps:
                    if bp and os.path.exists(bp):
                        avail_bp = bp
                        break
                if avail_bp:
                    (proc_hd, thread_hd,  proc_id, thread_id) = ProcUtil.CreateProc(avail_bp, paramstr=params)
                    #必须sleep 1
                    time.sleep(1)
                    whd = WinUtil.GetHWndByProcId(proc_id)
                    hwds.append(whd)
                    id_whds[wid] = whd
                    
                    
            ## 执行命令行命令
            if action == "command":
                cmdline = data.get("cmdline", None)
                if cmdline:
                    os.system(cmdline)
                    time.sleep(2)
                
            if action == "getwin":
                title = data.get("title", None)
                clsname = data.get("clsname", None)
                wid = data.get("id", None)
                ref_id = data.get("ref_id", None)
                if ref_id:  ## 高优先级
                    hwds.append(id_whds[ref_id])
                    id_whds[wid] = id_whds[ref_id]
                    continue

                if not wid:
                    print "[ERROR] GetWin Must Contain ID."
                    sys.exit(1)
                if not title and not clsname:
                    print "[ERROR] GetWin Must Assign One of (clsname, win_title) Or Both"
                    sys.exit(1)
                whd = WinUtil.GetWinByTitle(clsname=clsname, win_title=title)
                if not whd:
                    print "[WARN] GetWin Can't Find."
                    #sys.exit(1)
                if whd: WinUtil.SetWinCenter(whd)
                hwds.append(whd)
                id_whds[wid] = whd

            if action == "moveto":
                point = data.get("point", {})
                x = int(point.get("x", None))
                y = int(point.get("y", None))
                rect = WinUtil.GetCompRect(whd)
                point = (rect.left+x, rect.top+y)
                moveCurPos(point[0], point[1])
                time.sleep(2)
                # MouseUtil.MouseMove(point[0], point[1])
    
            if action == "lclick":
                clickLeftCur()
                MouseUtil.LClick()
                time.sleep(2)
            
            if action == "rclick":
                MouseUtil.RClick()
                
            if action == "settext":
                win32api.keybd_event(65,0,0,0)
                time.sleep(2)
                
            if action == "btnclick":
                title = data.get("title", None)
                ref_win_id = data.get("ref_win_id", None)
                if title == None:continue
                whd = None
                if not ref_win_id:
                    whd = hwds[-1]
                else:
                    whd = id_whds.get(ref_win_id, None)
                if not whd:
                    print "[WARN] BtnClick Can't Find Ref Win."
                    continue
                    #sys.exit(1)
                WinUtil.SetForegroundWindow(whd)
                btn = WinUtil.GetComponent(whd, win_title=title)
                (x, y) = WinUtil.GetCompCenterPos(btn)
                CursorUtil.SetCursorPos(x, y)
                MouseUtil.LClick()
                time.sleep(2)
            print
                
    except Exception:
            print traceback.format_exc()

def clickLeftCur():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN|win32con.MOUSEEVENTF_LEFTUP, 0, 0)

#移动鼠标到x,y
def moveCurPos(x,y):
    windll.user32.SetCursorPos(x, y)

def main():
    while True:
        rp = get_realpath()
        try:
            parser = OptionParser()
            parser.add_option("-c", "--conffile",  
                    action="store", dest="conf", default=None,  
                    help="configure file", metavar="CONFFILE")
            parser.add_option("-a", "--action",  
                    action="store", dest="action", default=None,  
                    help="action: such as start/stop which action define in conffile", metavar="ACTION")
            parser.add_option("-d", "--debug", dest="debug", default=False,
                    action="store_true", help="if debug, default is false")

            (options, args) = parser.parse_args()
            conffile = options.conf
            actionstr = options.action
            debug = options.debug
        
            if not conffile:
                parser.print_help()
                sys.exit(1)

            #conffile = os.path.abspath(conffile)
            conffile = rp + "\\etc\\" + conffile
            if os.path.exists(conffile) == False:
                parser.print_help()
                sys.exit(0)

            px = APPOpsXml(conffile)
            actions_def = px.get_actions()

            actionstr = str(actionstr).strip().lower()
            if actionstr not in actions_def:
                parser.print_help()
                sys.exit(1)

            action_steps = px.get_action_steps(actionstr)
            if not action_steps:
                print "Can Not Find Action Defined, Exit..."
                sys.exit(1)

            actions(action_steps)
            time.sleep(86400)
        except Exception as expt:
            print traceback.format_exc()
        
if __name__ == "__main__":
    main()
