import maya.cmds as mc

ta, ra = ["tx", "ty", "tz"], ["rx", "ry", "rz"]
atb = ta + ra #Attributes to bake
ABObj = [None, None]

def show_msg(msg):
    mc.confirmDialog(t="Messages", m=msg, b="OK")

#User Interface
def ui():
    mc.deleteUI("CBTool") if mc.window("CBTool", ex=1) else None
    wnd_name = mc.window("CBTool", t="CBTool", wh=[295, 144], s=0, mxb=0)
    main_layout = mc.columnLayout(bgc=[0.12, 0.1, 0.09])
    main_form = mc.formLayout(h=117)
    tabs_layout = mc.tabLayout(h=110, cc=lambda *args: change_tab(tabs_layout, main_form))
    tab1(tabs_layout)
    tab2(tabs_layout)
    tab3(tabs_layout)
    mc.formLayout(main_form, e=1, af=[(tabs_layout, 'top', 8), (tabs_layout, 'left', 10), (tabs_layout, 'right', 10)])
    mc.setParent(main_layout)
    about()
    mc.showWindow(wnd_name)
def change_tab(tabs_layout, main_form):
    current_tab_index = mc.tabLayout(tabs_layout, q=1, sti=1)
    if current_tab_index in [1, 2]:
        mc.tabLayout(tabs_layout, e=1, h=110)
        mc.formLayout(main_form, e=1, h=117)
        mc.window("CBTool", e=1, wh=[295, 144])
    elif current_tab_index == 3:
        mc.tabLayout(tabs_layout, e=1, h=155)
        mc.formLayout(main_form, e=1, h=163)
        mc.window("CBTool", e=1, wh=[295, 190])
def tab1(tabs_layout):
    tab = mc.columnLayout(adj=1)
    tc, rc, sbc = chkbox() #Translate, rotate, smart bake checkboxes = tc, rc, sbc
    mc.setParent(tab)
    btn(tc, rc, sbc) #Create Button & Get information from 3 checkboxes
    mc.setParent(tab)
    mc.tabLayout(tabs_layout, e=1, tl=[tab, "Reconstraint"])
    mc.setParent(tabs_layout)
def tab2(tabs_layout):
    tab = mc.columnLayout(adj=1)
    sbc = chkbox2()
    mc.setParent(tab)
    btn2_row1(sbc)
    mc.setParent(tab)
    btn2_row2(sbc)
    mc.setParent(tab)
    mc.tabLayout(tabs_layout, e=1, tl=[tab, "Rotate Order"])
    mc.setParent(tabs_layout)
def tab3(tabs_layout):
    tab = mc.columnLayout(adj=1)
    tc, rc = chkbox3()                      #Translate, rotate, smart bake checkboxes = tc, rc
    mc.setParent(tab)
    obj_in4()
    mc.setParent(tab)
    btn3(tc, rc)                            #Create Button & Get information from 2 checkboxes
    mc.tabLayout(tabs_layout, e=1, tl=[tab, "Match Transform"])
    mc.setParent(tabs_layout)

#Function Tab 1
def chkbox():
    chkbox_layout = mc.rowLayout(w=265, h=37, nc=4, bgc=[0.2, 0.2, 0.2], cat=[(1, "left", 15)])
    mc.columnLayout(w=80)
    tc = mc.checkBox(l="Translate")
    mc.setParent(chkbox_layout)
    mc.columnLayout(w=70)
    rc = mc.checkBox(l="Rotate")
    mc.setParent(chkbox_layout)
    sbc = mc.checkBox(l="Smart Bake")
    return tc, rc, sbc
def btn(tc, rc, sbc):
    btn_layout = mc.rowLayout(w=265, h=47, nc=3, bgc=[0.17, 0.17, 0.17], cat=[(1, "left", 13), (2, "both", 5), (3, "right", 0)]) #UI design for button
    mc.columnLayout(w=110, adj=1)
    loc_btn = mc.button(l="Create Locator", w=100, h=24, c=lambda x: loc(tc, rc, sbc), bgc=[0.26, 0.26, 0.26])   #lamba x: used in the context of events like button
    mc.setParent(btn_layout)
    mc.columnLayout(w=4)
    mc.separator(st='single', w=4, h=17, bgc=[0.5, 0.5, 0.5])
    mc.setParent(btn_layout)
    mc.columnLayout(w=110, adj=1)
    bkey_btn = mc.button(l="Bake key", w=100, h=24, c=lambda x: bkey(sbc), bgc=[0.26, 0.26, 0.26])
def loc(tc, rc, sbc):
    sl_obj = mc.ls(os=1)
    if not sl_obj:
        show_msg("Please select at least one object.")
        return
    tVal = mc.checkBox(tc, q=1, v=1)
    rVal = mc.checkBox(rc, q=1, v=1)
    sbVal = mc.checkBox(sbc, q=1, v=1)
    atb = [] + (ta if tVal else []) + (ra if rVal else [])         # Check attributes to bake
    locList = []                                                   # Locator list to bake all locators in 1 time
    for obj in sl_obj:
        loc = mc.spaceLocator(name=obj+'_Locator')
        locList.append(loc[0])
    for obj, loc in zip(sl_obj, locList):
        mc.parentConstraint(obj, loc)[0]
    mc.bakeResults(locList, t=(mc.playbackOptions(q=1, min=1), mc.playbackOptions(q=1, max=1)), at=atb, sr=[sbVal])
    for obj, loc in zip(sl_obj, locList):
        mc.pointConstraint(loc, obj, mo=1)[0] if tVal else None
        mc.orientConstraint(loc, obj, mo=1)[0] if rVal else None
def bkey(sbc):
    loc = [obj for obj in mc.ls() if obj.endswith("_Locator")]
    if not loc:
        show_msg("Make sure you have created a locator with the name *_Locator before executing Bake Key")
        return
    sbVal = mc.checkBox(sbc, q=1, v=1)
    objBk = [obj.replace("_Locator", "") for obj in loc if mc.objExists(obj)]           #objects to bake list = objBK
    if objBk:
        mc.bakeResults(objBk, t=(mc.playbackOptions(q=1, min=1), mc.playbackOptions(q=1, max=1)), at=atb, sr=[sbVal])
        mc.delete(loc)
        for obj in objBk:
            blendAttrs = [attr for attr in cmds.listAttr(obj) if attr.startswith("blendOrient") or attr.startswith("blendPoint")]
            if blendAttrs:
                for attr in blendAttrs:
                    cmds.deleteAttr(obj, at=attr)

#Function Tab 2
def sro(rotOrder, sbc):
    sl_obj = mc.ls(os=1)
    if not sl_obj:
        show_msg("Please select at least one object.")
        return
    locList = []
    constraintList = []
    sbVal = mc.checkBox(sbc, q=1, v=1)
    for obj in sl_obj:
        loc = mc.spaceLocator(name=obj+'_locator')
        locList.append(loc[0])
        constraint = mc.parentConstraint(obj, loc)
        constraintList.append(constraint)
    mc.bakeResults(locList, t=(mc.playbackOptions(q=1, min=1), mc.playbackOptions(q=1, max=1)), sr=[sbVal])
    for c in constraintList:
        mc.delete(c)
    for loc, obj in zip(locList, sl_obj):
        mc.orientConstraint(loc, obj)
    for obj in sl_obj:
        mc.setAttr(obj + '.rotateOrder', rotOrder)
    mc.bakeResults(sl_obj, t=(mc.playbackOptions(q=1, min=1), mc.playbackOptions(q=1, max=1)), at=ra, sr=[sbVal])
    mc.delete(locList)
    mc.select(sl_obj)
def chkbox2():
    row = mc.rowLayout(w=265, h=20, nc=4, bgc=[0.2, 0.2, 0.2])
    mc.columnLayout(w=8)
    mc.setParent(row)
    mc.columnLayout(adj=1)
    sbc = mc.checkBox(l="Smart Bake")
    mc.setParent(row)
    return sbc
def btn2_row1(sbc):
    row = mc.rowLayout(w=265, h=32, nc=4, bgc=[0.17, 0.17, 0.17], cat=[(1, "left",5), (2, "both", 5)])
    mc.columnLayout(w=80, adj=1)
    mc.button(l='xyz', h=20, w=50, c=lambda x: sro(0, sbc), bgc=[0.22, 0.22, 0.22])
    mc.setParent(row)
    mc.columnLayout(w=80, adj=1)
    mc.button(l='xzy', h=20, w=50, c=lambda x: sro(3, sbc), bgc=[0.22, 0.22, 0.22])
    mc.setParent(row)
    mc.columnLayout(w=80, adj=1)
    mc.button(l='yxz', h=20, w=50, c=lambda x: sro(4, sbc), bgc=[0.22, 0.22, 0.22])
    mc.setParent(row)
def btn2_row2(sbc):
    row = mc.rowLayout(w=265, h=32, nc=4, bgc=[0.17, 0.17, 0.17], cat=[(1, "left",5), (2, "both", 5), (3, "right", 0)])
    mc.columnLayout(w=80, adj=1)
    mc.button(l='yzx', h=20, w=50, c=lambda x: sro(1, sbc), bgc=[0.22, 0.22, 0.22])
    mc.setParent(row)
    mc.columnLayout(w=80, adj=1)
    mc.button(l='zxy', h=20, w=50, c=lambda x: sro(2, sbc), bgc=[0.22, 0.22, 0.22])
    mc.setParent(row)
    mc.columnLayout(w=80, adj=1)
    mc.button(l='zyx', h=20, w=50, c=lambda x: sro(5, sbc), bgc=[0.22, 0.22, 0.22])
    mc.setParent(row)

#Function Tab 3
def chkbox3():
    chkbox_layout = mc.rowLayout(w=265, h=30, nc=3, bgc=[0.2, 0.2, 0.2], cat=[(1, "left",40), (2, "both", 8)])
    mc.columnLayout(w=120)
    tc = mc.checkBox(l="Translate")
    mc.setParent(chkbox_layout)
    mc.columnLayout(w=120)
    rc = mc.checkBox(l="Rotate")
    return tc, rc
def obj_in4():
    in4_form = mc.formLayout(bgc=[0.18, 0.18, 0.18])
    in4_layout = mc.rowLayout(nc=3, cat=[(1, "left",30)])
    mc.columnLayout(w=100, adj=1)
    mc.button(h=15, w=50, l="Select A", c=lambda x: chk_in4(1, in4_txtfield1, in4_txtfield2), bgc=[0.27, 0.27, 0.27], al="center")
    in4_txtfield1 = mc.textFieldGrp(h=30, ed=0, cal=(1, "center"), adj=1, bgc=[0.1, 0.1, 0.1])
    mc.setParent(in4_layout)
    mc.columnLayout(w=100, adj=1)
    mc.button(h=15, w=50, l="Select B", c=lambda x: chk_in4(2, in4_txtfield1, in4_txtfield2), bgc=[0.27, 0.27, 0.27], al="center")
    in4_txtfield2 = mc.textFieldGrp(h=30, ed=0, cal=(1, "center"), adj=1, bgc=[0.1, 0.1, 0.1])
    mc.formLayout(in4_form, e=1, af=[(in4_layout, 'top', 5), (in4_layout, 'left', 2), (in4_layout, 'right', 2), (in4_layout, 'bottom', 3)])
def btn3(tc, rc):
    btn_layout = mc.rowLayout(w=265, h=42, nc=3, bgc=[0.15, 0.15, 0.15], cat=[(1, "left", 12), (2, "both", 5), (3, "right", 0)])
    mc.columnLayout(w=110, adj=1)
    loc_btn = mc.button(l="A to B", w=100, h=24, c=lambda x: amt(tc, rc, chk_tr=1), bgc=[0.26, 0.26, 0.26])
    mc.setParent(btn_layout)
    mc.columnLayout(w=4)
    mc.separator(st='single', w=4, h=17, bgc=[0.5, 0.5, 0.5])
    mc.setParent(btn_layout)
    mc.columnLayout(w=110, adj=1)
    bkey_btn = mc.button(l="B to A", w=100, h=24, c=lambda x: amt(tc, rc, chk_tr=0), bgc=[0.26, 0.26, 0.26])
def chk_in4(in4, in4_txtfield1, in4_txtfield2):
    global ABObj
    sl_obj = mc.ls(sl=1)
    if not sl_obj:
        show_msg("Please select an object.")
        return
    sl_obj = sl_obj[0]
    if in4 == 1:
        mc.textFieldGrp(in4_txtfield1, e=1, tx=sl_obj)
        ABObj[0] = sl_obj
    elif in4 == 2:
        mc.textFieldGrp(in4_txtfield2, e=1, tx=sl_obj)
        ABObj[1] = sl_obj
def amt(tc, rc, chk_tr=1): #Apply Match Transform
    global ABObj
    objA, objB = ABObj
    if objA is None or objB is None:
        show_msg("Please select objects A and B.")
        return
    tChk = mc.checkBox(tc, q=1, v=1)
    rChk = mc.checkBox(rc, q=1, v=1)
    if chk_tr:
        mc.matchTransform(objA, objB, pos=tChk, rot=rChk)
    else:
        mc.matchTransform(objB, objA, pos=tChk, rot=rChk)

#Version
def about():
    mc.rowLayout(h=28)
    mc.text(label="… CBTool version 0.3.35 …", align="right", fn="obliqueLabelFont", width=280)
    mc.setParent("..")

ui()