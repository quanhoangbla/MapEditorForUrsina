from ursina import *
from ursina.mesh_importer import *
from tkinter import simpledialog, messagebox, filedialog
import importlib

app=Ursina()

deleting=False

selecting=None
def toggle_vis(self:Entity):
    self.wireframe=not self.wireframe
    if not self.wireframe:
        self.clearRenderMode()
Entity.toggle_vis=toggle_vis

class DebugBehaviour():
    def __init__(self) -> None:
        self.entity:Entity
    def update(self):
        self.entity.on_click=self.toggle
        if selecting!=self: return
        if held_keys["shift"]:
            self.entity.scale_z += (held_keys['up arrow'] - held_keys['down arrow']) * (time.dt * (1 if held_keys['control'] else 5) if not held_keys['alt'] else 0)
            self.entity.scale_y += (held_keys['page up'] - held_keys['page down']) * (time.dt * (1 if held_keys['control'] else 5) if not held_keys['alt'] else 0)
            self.entity.scale_x += (held_keys['right arrow'] - held_keys['left arrow']) * (time.dt * (1 if held_keys['control'] else 5) if not held_keys['alt'] else 0)
        else:
            self.entity.z += (held_keys['up arrow'] - held_keys['down arrow']) * (time.dt * (1 if held_keys['control'] else 5) if not held_keys['alt'] else 0)
            self.entity.y += (held_keys['page up'] - held_keys['page down']) * (time.dt * (1 if held_keys['control'] else 5) if not held_keys['alt'] else 0)
            self.entity.x += (held_keys['right arrow'] - held_keys['left arrow']) * (time.dt * (1 if held_keys['control'] else 5) if not held_keys['alt'] else 0)

        self.entity.rotation_y += (held_keys['x'] - held_keys['z']) * time.dt * (10 if held_keys['control'] else 20)
        self.entity.rotation_x += (held_keys['c'] - held_keys['v']) * time.dt * (10 if held_keys['control'] else 20)
        self.entity.rotation_z += (held_keys['b'] - held_keys['n']) * time.dt * (10 if held_keys['control'] else 20)
    def input(self, key):
        if selecting!=self: return
        if key=='f':
            print(f'\'{self.entity.name}\' pos : {self.entity.position}')
            print(f'\'{self.entity.name}\' rot : {self.entity.rotation}')
        if held_keys["shift"]:
            self.entity.scale_z += (int(key=='up arrow') - int(key=='down arrow')) * held_keys['alt']
            self.entity.scale_y += (int(key=='page up') - int(key=='page down')) * held_keys['alt']
            self.entity.scale_x += (int(key=='right arrow') - int(key=='left arrow')) * held_keys['alt']
            if held_keys['alt'] and key != 'alt':
                self.entity.scale_x=int(self.entity.scale_x)
                self.entity.scale_y=int(self.entity.scale_y)
                self.entity.scale_z=int(self.entity.scale_z)
        else:
            self.entity.z += (int(key=='up arrow') - int(key=='down arrow')) * held_keys['alt']
            self.entity.y += (int(key=='page up') - int(key=='page down')) * held_keys['alt']
            self.entity.x += (int(key=='right arrow') - int(key=='left arrow')) * held_keys['alt']
            if held_keys['alt'] and key != 'alt':
                self.entity.x=int(self.entity.x)
                self.entity.y=int(self.entity.y)
                self.entity.z=int(self.entity.z)
    def toggle(self):
        global selecting
        if deleting:
            destroy(self.entity)
            destroy(self.entity.btn)
            objects.remove(self.entity)
        else:
            if selecting==self: selecting=None
            else: selecting=self

objects=[]

def addnew():
    name=simpledialog.askstring("Map Editor", "Enter Object's name")
    model=simpledialog.askstring("Map Editor", "Enter Object's Model name")
    texture=simpledialog.askstring("Map Editor", "Enter Object's Texture name")
    clr=None
    try:
        if isinstance(eval(texture), color.Color): clr=eval(texture)
    except: pass
    collider=simpledialog.askstring("Map Editor", "Enter Object's Collider type")
    double_sided=messagebox.askyesno("Map Editor", "Double Sided?")
    try:
        i=Entity(name=name, model=model if model!="" else "cube", double_sided=double_sided)
        if collider!='': i.collider=collider
        if texture!='': i.texture=texture
        if clr: i.color=clr
        if i.model==None: i.model='cube'
        i.add_script(DebugBehaviour())
        objects.append(i)
    except:pass
    refresh_container()

def toggleDelete():
    global deleting
    deleting = not deleting
    tdm.color=color.green if deleting else color.red
    tdm.highlight_color=tdm.color.tint(.2)
    tdm.pressed_color=tdm.color.tint(-.2)

def save():
    file=filedialog.asksaveasfile(defaultextension='.mes', filetypes=[("Map Editor Scene", "*.mes")],)
    if file:
        code=""
        for i in objects:
            i:Entity
            repra=repr(i)
            if i.collider and not 'collider=' in repra:
                repra=repra[:-1]+f'collider=\'{i.collider.name}\', )'
            code+=repra+'\n'
        file.write(code)

OBJECTS_PER_PAGE=5

def pg(i):
    global current_page
    if i==1:
        current_page=min(ceil(len(objects)/OBJECTS_PER_PAGE)-1, current_page+i)
    else: current_page=max(0, current_page+i)
    print(current_page)
    refresh_container()
container=Entity(model=Quad(.1, aspect=.7), color=color.black33, parent=camera.ui, scale=(.7,1), x=0.6479293, eternal=True)
Button('Previous', position=Vec3(0.4540579, -0.36839267, -1.3447969), color=color.white, on_click=lambda:pg(-1), scale=(.25,.1), text_color=color.black, eternal=True)
Button('Next', position=Vec3(0.736449, -0.36839267, -1.3447969), color=color.white, on_click=lambda:pg(1), scale=(.25,.1), text_color=color.black, eternal=True)
current_page=0
container_o=[]

def buttonthing(self, key):
    if self.disabled or not self.model:
        return

    if key == 'left mouse down':
        if self.hovered:
            self.model.setColorScale(self.pressed_color)
            self.model.setScale(Vec3(self.pressed_scale, self.pressed_scale, 1))
            if self.pressed_sound:
                if isinstance(self.pressed_sound, Audio):
                    self.pressed_sound.play()
                elif isinstance(self.pressed_sound, str):
                    Audio(self.pressed_sound, auto_destroy=True)

    if key == 'left mouse up':
        if self.hovered:
            self.model.setColorScale(self.highlight_color)
            self.model.setScale(Vec3(self.highlight_scale, self.highlight_scale, 1))
        else:
            self.model.setColorScale(self.color)
            self.model.setScale(Vec3(1,1,1))
    if key == 'right mouse down':
        if self.hovered:
            self.model.setColorScale(self.pressed_color)
            self.entity.scripts[0].toggle()

def refresh_container():
    for i in container_o:
        destroy(i)
    container_o.clear()
    for i in range(current_page*OBJECTS_PER_PAGE, min((current_page+1)*OBJECTS_PER_PAGE,len(objects))):
        if objects[i]:
            btn=Button(objects[i].name, position=Vec3(0.6342687, 0.40175405*(1-i/3), -0.90489095), on_click=objects[i].toggle_vis, color=color.white, scale=(.5,.1), text_color=color.black)
            btn.input=lambda x:buttonthing(btn,x)
            container_o.append(btn)
            btn.entity=objects[i]
            objects[i].btn=btn
def load():
    file=filedialog.askopenfile(defaultextension='mes', filetypes=[("Map Editor Scene", "*.mes")])
    if file:
        scene.clear()
        camera.overlay.color=color.clear
        exec(file.read())
        for i in scene.entities:
            i:Entity
            if not i.eternal:
                objects.append(i)
                i.add_script(DebugBehaviour())
        refresh_container()
Entity(model=Quad(.1, aspect=.7), color=color.black33, parent=camera.ui, scale=(.7,1), x=-0.6479293, eternal=True)
Button('Add new Object', position=Vec3(-0.61267745, 0.39322376, -0.8950644), color=color.white, on_click=addnew, scale=(.5,.1), text_color=color.black, eternal=True)
tdm=Button('Toggle Delete Mode', position=Vec3(-0.61267745, 0.19322376, -0.8950644), on_click=toggleDelete, scale=(.5,.1), text_color=color.black, eternal=True)
tdm.color=color.green if deleting else color.red
tdm.highlight_color=tdm.color.tint(.2)
tdm.pressed_color=tdm.color.tint(-.2)

Button('Save', position=Vec3(-0.61267745, -0.19322376, -0.8950644), color=color.white, on_click=save, scale=(.5,.1), text_color=color.black, eternal=True)
Button('Load', position=Vec3(-0.61267745, -0.30322376, -0.8950644), color=color.white, on_click=load, scale=(.5,.1), text_color=color.black, eternal=True)
cs=Text('Current Selecting : ', origin=(0,0), eternal=True, position=Vec3(0.61267745,-.25,0))
def update():
    if selecting==None: cs.text=f'Current Selecting : None'
    else: cs.text=f'Current Selecting : {selecting.entity.name}'
Entity(model=Grid(512,512), rotation_x=90, scale=512, color=color.white33, enabled=True, x=.5, z=.5, y=-.5, eternal=True)

Sky(eternal=True)
EditorCamera(eternal=True)

app.run()