import bpy
from bpy.types import Panel, Operator

# Custom RoughFruitSkinOperator
class MaterialOperator(Operator):
    bl_idname = "fruit.rough_skin"
    bl_label = "Rough Fruit Skin Operator"
    
    def execute(self, context):
        ob = context.active_object
        
        # Get material
        mat = bpy.data.materials.get("fruit_roughSkin")
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="fruit_roughSkin")
        
        # Assign it to object
        if ob.data.materials:
            # assign to 1st material slot
            ob.data.materials[0] = mat
        else:
            # no slots
            ob.data.materials.append(mat)
        
        # Make a voronoi texture node
        voronoiTexture1 = mat.node_tree.nodes.new(type = 'ShaderNodeTexVoronoi')
        voronoiTexture1.inputs['Scale'].default_value = 400
        
        # Make another voronoi texture node
        voronoiTexture2 = mat.node_tree.nodes.new(type = 'ShaderNodeTexVoronoi')
        voronoiTexture2.inputs['Scale'].default_value = 140
        voronoiTexture2.location.y = -200
        
        # Make a texture coordinate node
        texCoord = mat.node_tree.nodes.new(type = 'ShaderNodeTexCoord')
        texCoord.location.x = -300
        
        # Link Texture Coordinate to the Voronoi Texture nodes
        uv = texCoord.outputs[2]
        mat.node_tree.links.new(uv, voronoiTexture1.inputs[0])
        mat.node_tree.links.new(uv, voronoiTexture2.inputs[0])
        
        # Add screen node
        screen = mat.node_tree.nodes.new(type = 'ShaderNodeMixRGB')
        screen.blend_type = 'SCREEN'
        screen.inputs["Fac"].default_value = 0.3
        screen.location.x = 300
        screen.location.y = -200
        
        # Link Voronoi Texture nodes to Screen 
        mat.node_tree.links.new(voronoiTexture1.outputs[0], screen.inputs[1])
        mat.node_tree.links.new(voronoiTexture2.outputs[0], screen.inputs[2])
        
        # Add invert node
        invert = mat.node_tree.nodes.new(type = 'ShaderNodeInvert')
        invert.location.x = 500
        invert.location.y = -100
        
        # Connect screen to invert
        mat.node_tree.links.new(screen.outputs[0], invert.inputs[1])
        
        # Add multiply node
        multiply = mat.node_tree.nodes.new(type = 'ShaderNodeMixRGB')
        multiply.blend_type = 'MULTIPLY'
        multiply.inputs["Fac"].default_value = 0.05
        multiply.inputs["Color1"].default_value = (1.0, 1.0, 1.0, 1.0)
        multiply.location.x = 700
        multiply.location.y = -100
        
        # Connect invert to multiply
        mat.node_tree.links.new(invert.outputs[0], multiply.inputs[2])
        
        # Add noise texture
        noiseTexture = mat.node_tree.nodes.new(type = 'ShaderNodeTexNoise')
        noiseTexture.location.y = 300
        
        # Add overlay node
        overlay = mat.node_tree.nodes.new(type = 'ShaderNodeMixRGB')
        overlay.blend_type = 'OVERLAY'
        overlay.inputs["Fac"].default_value = 0.3
        overlay.inputs["Color1"].default_value = (1.0, 0.212, 0.0, 1.0)
        overlay.location.x = 200
        overlay.location.y = 300
        
        # Connect noise to overlay
        mat.node_tree.links.new(noiseTexture.outputs[0], overlay.inputs[2])
        
        # Add Diffuse BSDF
        diffuse = mat.node_tree.nodes.new(type = 'ShaderNodeBsdfDiffuse')
        diffuse.location.x = 400
        diffuse.location.y = 300
        
        # Connect overlay to Diffuse
        mat.node_tree.links.new(overlay.outputs[0], diffuse.inputs[0])
        
        # Add Glossy BSDF
        glossy = mat.node_tree.nodes.new(type = 'ShaderNodeBsdfGlossy')
        glossy.distribution = "BECKMANN"
        glossy.location.x = 400
        glossy.location.y = 100
        
        # Add Mix Shader
        mix = mat.node_tree.nodes.new(type = 'ShaderNodeMixShader')
        mix.inputs["Fac"].default_value = 0.1
        mix.location.x = 700
        mix.location.y = 100
        
        # Connect the BSDFs to the Mix Shader
        mat.node_tree.links.new(diffuse.outputs[0], mix.inputs[1])
        mat.node_tree.links.new(glossy.outputs[0], mix.inputs[2])
        
        # Add Material Output
        matOut = mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
        matOut.location.x = 1000
        
        # Connect Mix Shader to the output
        mat.node_tree.links.new(mix.outputs[0], matOut.inputs[0])
        
        # Connect multiply to the output
        mat.node_tree.links.new(multiply.outputs[0],matOut.inputs[2])
        
        return {"FINISHED"}
    

# Class for the panel, derived by the Panel
class RoughFruitSkin(Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_label = 'Rough Fruit Skin'
    bl_context = 'material'
    bl_category = 'Fruit'
    
    # Add UI elements here
    def draw(self, context):
        layout = self.layout
        layout.operator("fruit.rough_skin", text='Add rough skin')

# Register
def register():
    bpy.utils.register_class(MaterialOperator)
    bpy.utils.register_class(RoughFruitSkin)
    
# Unregister
def unregister():
    bpy.utils.register_class(MaterialOperator)
    bpy.utils.unregister_class(RoughFruitSkin)

# Needed to run script in Text Editor
if __name__ == '__main__':
    register()