import bpy
import bmesh
import math

imageName = 'DhPb'

print ('\Converting to singular texture\n')


colors = []


def to_hex(c):
    if c < 0.0031308:
        srgb = 0.0 if c < 0.0 else c * 12.92
    else:
        srgb = 1.055 * math.pow(c, 1.0 / 2.4) - 0.055

    return hex(max(min(int(srgb * 255 + 0.5), 255), 0))

def toHexGam(r,g,b):
   
    rgb = [r,g,b]
    result = ""
    i=0
    while i < 3:
        val = str(to_hex(rgb[i]))
        val = val[2:]
        if len(val) == 1:
            val += val
        result+=val
        i+=1
    return result

def toHexLin(r,g,b):
    r2 = int(r * 255)
    g2 = int(g * 255)
    b2 = int(b * 255)
    hex = '%02x%02x%02x' % (r2, g2, b2)
    #print('R: ', r, 'G:, ', g, 'B: ', b, '   Hex: ', hex)
    return hex

def toRGB(hex):
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    return rgb

for ob in bpy.context.selected_editable_objects:
    mesh = ob.data
    
    for f in mesh.polygons:  # iterate over faces
        #print("face", f.index, "material_index", f.material_index)
        slot = ob.material_slots[f.material_index]
        mat = slot.material
        if mat is not None:
            col = mat.diffuse_color
            hexGam = toHexGam(col[0], col[1], col[2])
          
            if(not (hexGam in colors)):
                colors.append(hexGam)
                print('R: ', col[0], 'G:, ', col[1], 'B: ', col[2], '   Hex: ', hex)

        else:
            print("No mat in slot", f.material_index)
        
    

#--Create The image--
size = 1
print('Total Colours: ', len(colors))
for i in range(12):
    if(size*size) >= len(colors):
        print('Image size is ', size, 'x', size)
        break
    size = size * 2

image = bpy.data.images.new("imageName", alpha=True, width=size, height=size)
image.filepath_raw = "//" + imageName + ".png"
image.file_format = 'PNG'


for x in range(size):
    for y in range(size):
        pixStart = (x*size + y) * 4
        image.pixels[pixStart : pixStart + 4 ] = (0, 0, 0, 1)
        

#--assign the pixels the correct colors--
print("Creating Image")
pixIndex = 0  
for col in colors:
    r, g, b = toRGB(col)
    
    pixStart = (pixIndex) * 4
    image.pixels[pixStart : pixStart + 4 ] = (r / 255, g/255, b/255, 1)
    #print('R: ', r / 255, 'G:, ', g /255, 'B: ',b/255, '   Hex: ', col)
    pixIndex = pixIndex + 1
        

image.save()

print('Image saved to: ',imageName,'.png' )

for ob in bpy.context.selected_editable_objects:
    mesh = ob.data

    #remove existing uvs
    alluvcount = len(ob.data.uv_layers)
    for uv in range(alluvcount):
        ob.data.uv_layers.remove(ob.data.uv_layers[alluvcount - uv - 1])
        
         
    #creat new uv layer  
    uvlayer = mesh.uv_layers.new() 
    mesh.uv_layers.active = uvlayer  
    

    for f in mesh.polygons:
        
        slot = ob.material_slots[f.material_index]
        mat = slot.material
        col = mat.diffuse_color
        hexColor = toHexGam(col[0], col[1], col[2])
        for vert_idx, loop_idx in zip(f.vertices, f.loop_indices):
           
            index = colors.index(hexColor)
            increment = 1 / size
            halfinc = increment / 2
            height = math.floor(index / size) * increment + halfinc
            length = (index % size) * increment + halfinc
            uvlayer.data[loop_idx].uv = (length, height)
    
    
    
for ob in bpy.context.selected_editable_objects:
    ob.active_material_index = 0
    for i in range(len(ob.material_slots)):
        bpy.ops.object.material_slot_remove({'object': ob})
