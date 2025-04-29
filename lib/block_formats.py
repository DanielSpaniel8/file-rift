multiline_strs = ["String"]
compile_tags = ["Bytes"]


file_types = ["fr", "scene", "scl", "gdata", "gopt", "gplayer", "gstate", "scmap", "sounds", "fnt", "atlas"]


block_formats = {

    # filetypes section

    "fr": {
        "Name": ("0a", ""),
        "Template": ("12", "", "ObjectTemplate"),
        "ImportedLibrary": ("1a", ""),
        "Texture": ("22", "", "Texture"),
        "Program": ("2a", "", "Program"),

        "Object": ("0a", "", "SceneObject"),
        "ObjectLibrary": ("12", "", "ObjectLibrary"),
        "Bounds": ("1a", "", "SceneBounds"),
        "Group" : ("22", "", "SceneObjectGroup"),
        "OnLoad": ("2a", "", "Program"),

        "Item": ("0a", "", "Item"),
        "Skill": ("12", "", "Skill"),
        "Quest": ("1a", "", "Quest"),
        "EntityClass": ("22", "", "EntityClass"),
        "GuideTarget": ("2a", "", "GuideTarget"),

        "Playlist": ("0a", "", "MusicPlaylist"),
        "MusicEnabled": ("10", ""),
        "SoundEnabled": ("18", ""),
        "MusicVolume": ("25", ""),
        "SoundVolume": ("2d", ""),
        "PhoneControlsLayout": ("32", "", "GUIViewLayout"),
        "PadControlsLayout": ("3a", "", "GUIViewLayout"),
        "GuideUnlocked": ("40", ""),
        "CoinDoublerUnlocked": ("48", ""),
        "NoAdsUnlocked": ("50", ""),

        "Name": ("0a", ""),
        "ExperienceLevel": ("10", ""),
        "TimePlayed": ("19", ""),
        "GameState": ("22", "", "GameState"),
        "EquippedWeaponName": ("2a", ""),
        "EquippedArmorName": ("32", ""),
        "WeaponTrinketName": ("3a", ""),
        "ArmorTrinketName": ("42", ""),
        "CurrentLevelTitle": ("4a", ""),
        "LastPlayedTime": ("52", "", "DateTime"),
        "PercentCompleted": ("5d", ""),
        "Counter": ("62", "", "PlayerProfile_Counter"),
        "CheatEnabled": ("68", ""),
        "Identifier": ("72", ""),

        "CharacterState": ("0a", "", "CharacterState"),
        "LevelState": ("12", "", "LevelState"),
        "CurrentLevel": ("1a", ""),
        "CurrentSpawnPoint": ("22", ""),
        "CurrentMapNodeName": ("2a", ""),
        "QuestState": ("3a", "", "QuestState"),
        "Properties": ("42", "", "StateProperties"),
        "SelectedMenuTab": ("4a", ""),
        "CarriedObjectTemplate": ("52", ""),
        "CarriedObjectIdentifier": ("5a", ""),
        "QuestText": ("62", "", "QuestText"),
        "PreviousPortalLevel": ("6a", ""),
        "MenuButtonFlashing": ("70", ""),
        "SkillToggleButtonFlashing": ("78", ""),
        "FlashingItemName": ("82", ""),
        "FlashingSkillName": ("8a", ""),
        "GuideEnabled": ("90", ""),
        "GuideToggled": ("98", ""),
        "CoinDoublerEnabled": ("a0", ""),
        "CoinDoublerToggled": ("a8", ""),

        "Zone": ("12", "", "MapZone"),

        "Effect": ("0a", "", "SoundEffect"),

        "Name": ("0a", ""),
        "Texture": ("12", "", "Texture"),
        "Glyph": ("1a", "", "Font_Glyph"),
        "Kerning": ("22", ""),
        "Height": ("28", ""),
        "BoundingBox": ("32", "", "Rectangle"),

        "Name": ("0a", ""),
        "PixelFormat": ("10", ""),
        "Subtexture": ("1a", "", "Texture_Subtexture"),
        "ImageType": ("20", ""),
        "ConversionInfo": ("2a", "", "Texture_ConversionInfo"),
    },

    "scl": {
        "Name": ("0a", ""),
        "Template": ("12", "", "ObjectTemplate"),
        "ImportedLibrary": ("1a", ""),
        "Texture": ("22", "", "Texture"),
        "Program": ("2a", "", "Program"),
    },

    "scene" : {
        "Object": ("0a", "", "SceneObject"),
        "ObjectLibrary": ("12", "", "ObjectLibrary"),
        "Bounds": ("1a", "", "SceneBounds"),
        "Group" : ("22", "", "SceneObjectGroup"),
        "OnLoad": ("2a", "", "Program"),
    },

    "gdata": {
        "Item": ("0a", "", "Item"),
        "Skill": ("12", "", "Skill"),
        "Quest": ("1a", "", "Quest"),
        "EntityClass": ("22", "", "EntityClass"),
        "GuideTarget": ("2a", "", "GuideTarget"),
    },

    "gopt": {
        "Playlist": ("0a", "", "MusicPlaylist"),
        "MusicEnabled": ("10", ""),
        "SoundEnabled": ("18", ""),
        "MusicVolume": ("25", ""),
        "SoundVolume": ("2d", ""),
        "PhoneControlsLayout": ("32", "", "GUIViewLayout"),
        "PadControlsLayout": ("3a", "", "GUIViewLayout"),
        "GuideUnlocked": ("40", ""),
        "CoinDoublerUnlocked": ("48", ""),
        "NoAdsUnlocked": ("50", ""),
    },

    "gplayer": {
        "Name": ("0a", ""),
        "ExperienceLevel": ("10", ""),
        "TimePlayed": ("19", ""),
        "GameState": ("22", "", "GameState"),
        "EquippedWeaponName": ("2a", ""),
        "EquippedArmorName": ("32", ""),
        "WeaponTrinketName": ("3a", ""),
        "ArmorTrinketName": ("42", ""),
        "CurrentLevelTitle": ("4a", ""),
        "LastPlayedTime": ("52", "", "DateTime"),
        "PercentCompleted": ("5d", ""),
        "Counter": ("62", "", "PlayerProfile_Counter"),
        "CheatEnabled": ("68", ""),
        "Identifier": ("72", ""),
    },

    "gstate": {
        "CharacterState": ("0a", "", "CharacterState"),
        "LevelState": ("12", "", "LevelState"),
        "CurrentLevel": ("1a", ""),
        "CurrentSpawnPoint": ("22", ""),
        "CurrentMapNodeName": ("2a", ""),
        "QuestState": ("3a", "", "QuestState"),
        "Properties": ("42", "", "StateProperties"),
        "SelectedMenuTab": ("4a", ""),
        "CarriedObjectTemplate": ("52", ""),
        "CarriedObjectIdentifier": ("5a", ""),
        "QuestText": ("62", "", "QuestText"),
        "PreviousPortalLevel": ("6a", ""),
        "MenuButtonFlashing": ("70", ""),
        "SkillToggleButtonFlashing": ("78", ""),
        "FlashingItemName": ("82", ""),
        "FlashingSkillName": ("8a", ""),
        "GuideEnabled": ("90", ""),
        "GuideToggled": ("98", ""),
        "CoinDoublerEnabled": ("a0", ""),
        "CoinDoublerToggled": ("a8", ""),
    },

    "scmap": {
        "Zone": ("12", "", "MapZone"),
    },

    "sounds": {
        "Effect": ("0a", "", "SoundEffect"),
    },

    "fnt": {
        "Name": ("0a", ""),
        "Texture": ("12", "", "Texture"),
        "Glyph": ("1a", "", "Font_Glyph"),
        "Kerning": ("22", ""),
        "Height": ("28", ""),
        "BoundingBox": ("32", "", "Rectangle"),
    },

    "atlas": {
        "Name": ("0a", ""),
        "PixelFormat": ("10", ""),
        "Subtexture": ("1a", "", "Texture_Subtexture"),
        "ImageType": ("20", ""),
        "ConversionInfo": ("2a", "", "Texture_ConversionInfo"),
    },

    # scene section

    "Scene" : {
        "Object": ("0a", "", "SceneObject"),
        "ObjectLibrary": ("12", "", "ObjectLibrary"),
        "Bounds": ("1a", "", "SceneBounds"),
        "Group": ("22", "", "SceneObjectGroup"),
        "OnLoad": ("2a", "", "Program"),
    },

    "SceneObject" : {
        "TemplateName": ("0a", "[optional] reference to a template to initialize the object from"),
        "Identifier": ("12", "used to refer to this object"),
        "Component": ("1a", "", "Component"),
        "Position": ("22", "", "Vector2"),
        "Depth": ("2d", ""),
        "Rotation": ("35", ""),
        "Scaling": ("3d", ""),
        "LocalAabb": ("42", "", "Rectangle"),
        "Hidden": ("48", ""),
        "OnLoad": ("52", "", "Program"),
    },

    "ObjectLibrary": {
        "Name": ("0a", ""),
        "Template": ("12", "", "ObjectTemplate"),
        "ImportedLibrary": ("1a", ""),
        "Texture": ("22", "", "Texture"),
        "Program": ("2a", "", "Program"),
    },

    "ObjectTemplate": {
        "Object": ("0a", "", "SceneObject"),
        "Scaling": ("15", ""),
    },

    "SceneBounds" : {
        "Top" : ("0d", "level max height"),
        "Left" : ("15", ""),
        "Right" : ("1d", ""),
        "Bottom" : ("25", ""),
    },

    "SceneObjectGroup": {
        "Identifier": ("0a", ""),
        "ObjectIdentifier": ("12", ""),
        "Hidden": ("18", ""),
        "OnLoad": ("22", "", "Program"),
        "CanBecomeActive": ("28", ""),
        "Locked": ("30", ""),
    },

    # gamedata section

    "GameData": {
        "Item": ("0a", "", "Item"),
        "Skill": ("12", "", "Skill"),
        "Quest": ("1a", "", "Quest"),
        "EntityClass": ("22", "", "EntityClass"),
        "GuideTarget": ("2a", "", "GuideTarget"),
    },

    "Item": {
        # "CONSUMABLE": 1
        #     "WEAPON": 2
        #     "ARMOR": 3
        #     "TRINKET": 4
        #     "QUEST": 5
        #     "Type_MIN": 1
        #     "Type_MAX": 5
        #     "Type_ARRAYSIZE": 6
        "Type": ("08", ""),
        "Name": ("12", ""),
        "Title": ("1a", ""),
        "ShortDescription": ("22", ""),
        "Description": ("2a", ""),
        "Unique": ("30", ""),
        "MinDamage": ("38", ""),
        "MaxDamage": ("40", ""),
        "Level": ("48", ""),
    },

    "Skill": {
        "Name": ("0a", ""),
        "Title": ("12", ""),
        "Description": ("1a", ""),
        "ManaCost": ("20", ""),
        "MinDamage": ("28", ""),
        "MaxDamage": ("30", ""),
    },

    "Quest": {
        "Name": ("0a", ""),
        "Title": ("12", ""),
        "FollowUpQuest": ("1a", ""),
        "MapLocation": ("22", ""),
    },

    "EntityClass": {
        "Name": ("0a", ""),
        "Title": ("12", ""),
        "LevelHidden": ("18", ""),
        "Freezable": ("20", ""),
        "Stunnable": ("28", ""),
        "Grabbable": ("30", ""),
        "MagicResistance": ("3d", ""),
        "PhysicalResistance": ("45", ""),
    },

    "GuideTarget": {
        # "UNKNOWN": 0
        #     "QUESTGET": 1
        #     "QUEST": 2
        #     "SPELL": 3
        #     "KEY": 4
        #     "Type_MIN": 0
        #     "Type_MAX": 4
        #     "Type_ARRAYSIZE": 5
        "Type": ("08", ""),
        "Name": ("12", ""),
        "LevelName": ("1a", ""),
        "ObjectIdentifier": ("22", ""),
        "CarryObjectIdentifier": ("2a", ""),
        "ShowOnlyAfterSceneLoad": ("30", ""),
        "PortalHint": ("3a", "", "GuideTarget_LevelObject"),
    },

    "GuideTarget_LevelObject": {
        "LevelName": ("0a", ""),
        "ObjectIdentifier": ("12", ""),
    },

    # gameoptions section


    "GameOptions": {
        "Playlist": ("0a", "", "MusicPlaylist"),
        "MusicEnabled": ("10", ""),
        "SoundEnabled": ("unk", ""),
        "MusicVolume": ("unk", ""),
        "SoundVolume": ("unk", ""),
        "PhoneControlsLayout": ("32", "", "GUIViewLayout"),
        "PadControlsLayout": ("3a", "", "GUIViewLayout"),
        "GuideUnlocked": ("unk", ""),
        "CoinDoublerUnlocked": ("unk", ""),
        "NoAdsUnlocked": ("unk", ""),
    },

    "MusicPlaylist": {
        "Name": ("0a", ""),
        "Track": ("12", "", "MusicTrack"),
    },

    "MusicTrack": {
        "ResourceName": ("0a", ""),
        "Volume": ("15", ""),
    },

    "GUIViewLayout": {
        "Identifier": ("0a", ""),
        "Subview": ("12", "", "GUIViewLayout"),
        "Margins": ("1a", "", "GUIMargins"),
    },

    "GUIMargins": {
        "Left": ("0d", ""),
        "Right": ("15", ""),
        "Bottom": ("1d", ""),
        "Top": ("25", ""),
    },

    # player profile section

    "PlayerProfile": {
        "Name": ("0a", ""),
        "ExperienceLevel": ("10", ""),
        "TimePlayed": ("19", ""),
        "GameState": ("22", "", "GameState"),
        "EquippedWeaponName": ("2a", ""),
        "EquippedArmorName": ("32", ""),
        "WeaponTrinketName": ("3a", ""),
        "ArmorTrinketName": ("42", ""),
        "CurrentLevelTitle": ("4a", ""),
        "LastPlayedTime": ("52", "", "DateTime"),
        "PercentCompleted": ("5d", ""),
        "Counter": ("62", "", "PlayerProfile_Counter"),
        "CheatEnabled": ("68", ""),
        "Identifier": ("72", ""),
    },

    "GameState": {
        "CharacterState": ("0a", "", "CharacterState"),
        "LevelState": ("12", "", "LevelState"),
        "CurrentLevel": ("1a", ""),
        "CurrentSpawnPoint": ("22", ""),
        "CurrentMapNodeName": ("2a", ""),
        "QuestState": ("3a", "", "QuestState"),
        "Properties": ("42", "", "StateProperties"),
        "SelectedMenuTab": ("4a", ""),
        "CarriedObjectTemplate": ("52", ""),
        "CarriedObjectIdentifier": ("5a", ""),
        "QuestText": ("62", "", "QuestText"),
        "PreviousPortalLevel": ("6a", ""),
        "MenuButtonFlashing": ("70", ""),
        "SkillToggleButtonFlashing": ("78", ""),
        "FlashingItemName": ("82", ""),
        "FlashingSkillName": ("8a", ""),
        "GuideEnabled": ("90", ""),
        "GuideToggled": ("98", ""),
        "CoinDoublerEnabled": ("a0", ""),
        "CoinDoublerToggled": ("a8", ""),
    },

    "CharacterState": {
        "CurrentHealth": ("10", ""),
        "CurrentMana": ("20", ""),
        "CurrentCoins": ("28", ""),
        "ExperiencePoints": ("30", ""),
        "ExperienceLevel": ("38", ""),
        "Item": ("5a", "", "CharacterState_ItemState"),
        "EquippedWeapon": ("62", ""),
        "EquippedArmor": ("6a", ""),
        "Skill": ("7a", ""),
        "CurrentSkill": ("82", ""),
        "WeaponTrinket": ("8a", ""),
        "ArmorTrinket": ("92", ""),
        "SkillTrinket": ("9a", ""),
        "HealthAttribute": ("a0", ""),
        "AttackAttribute": ("a8", ""),
        "MagicAttribute": ("b0", ""),
    },

    "CharacterState_ItemState": {
        "Name": ("0a", ""),
        "Count": ("10", ""),
    },

    "LevelState": {
        "LevelName": ("0a", ""),
        "Visited": ("10", ""),
        "Properties": ("1a", "", "StateProperties"),
        "NumTreasures": ("20", ""),
        "TreasuresFound": ("28", ""),
    },

    "StateProperties": {
        "Flag": ("0a", ""),
    },

    "QuestState": {
        "QuestName": ("0a", ""),
        "Completed": ("10", ""),
    },

    "QuestText": {
        "QuestName": ("0a", ""),
        "Line": ("12", ""),
    },

    "PlayerProfile_Counter": {
        "Name": ("0a", ""),
        "Value": ("10", ""),
    },

    # map section

    "Map": {
        "Zone": ("12", "", "MapZone"),
    },

    "MapZone": {
        "Name": ("0a", ""),
        "Title": ("12", ""),
        "Node": ("1a", "", "MapNode"),
        "ExperienceLevel": ("20", ""),
        "Music": ("2a", ""),
    },

    "MapNode": {
        # "TYPE_DEFAULT": 0
        # "TYPE_TOWN": 1
        # "TYPE_WAYPOINT": 2
        # "TYPE_BOSS": 3
        # "Type_MIN": 0
        # "Type_MAX": 3
        # "Type_ARRAYSIZE": 4
        "Position": ("unk", ""),
        "LevelName": ("12", ""),
        "Portal": ("1a", "", "MapNode_Portal"),
        "Type": ("20", ""),
        "Hidden": ("28", ""),
        "ExperienceLevel": ("30", ""),
        "Music": ("3a", ""),
        "HasPortal": ("40", ""),
        "NumTreasures": ("48", ""),
        "Title": ("52", ""),
        "IgnoreInStatistics": ("58", ""),
    },

    "MapNode_Portal": {
        # "E": 1
        # "NE": 2
        # "N": 3
        # "NW": 4
        # "W": 5
        # "SW": 6
        # "S": 7
        # "SE": 8
        # "Direction_MIN": 1
        # "Direction_MAX": 8
        # "Direction_ARRAYSIZE": 9
        # "FORWARDS_AND_BACKWARDS": 0
        # "FORWARDS_ONLY": 1
        # "BACKWARDS_ONLY": 2
        # "PassDirection_MIN": 0
        # "PassDirection_MAX": 2
        # "PassDirection_ARRAYSIZE": 3
        "DestinationName": ("0a", ""),
        "Direction": ("10", ""),
        "PassDirection": ("18", ""),
        "IgnoreInNodePositioning": ("20", ""),
    },

    # sound section

    "SoundLibrary": {
        "Effect": ("0a", "", "SoundEffect"),
    },

    "SoundEffect": {
        "Name": ("0a", ""),
        "ResourceName": ("12", ""),
        "Volume": ("1d", ""),
        "MinPlayInterval": ("25", ""),
    },

    # font section

    "Font": {
        "Name": ("0a", ""),
        "Texture": ("12", "", "Texture"),
        "Glyph": ("1a", "", "Font_Glyph"),
        "Kerning": ("22", ""),
        "Height": ("28", ""),
        "BoundingBox": ("32", "", "Rectangle"),
    },

    "Texture": {
        "Name": ("0a", ""),
        "PixelFormat": ("10", ""),
        "Subtexture": ("1a", "", "Texture_Subtexture"),
        "ImageType": ("20", ""),
        "ConversionInfo": ("2a", "", "Texture_ConversionInfo"),
    },

    "Font_Glyph": {
        "CharCode": ("08", ""),
        "DrawBounds": ("12", "", "Rectangle"),
        "HorizAdvance": ("18", ""),
        "TextureBounds": ("22", "", "Rectangle"),
    },

    "Texture_Subtexture": {
        "Name": ("0a", ""),
        "Bounds": ("12", "", "Rectangle"),
        "Resolution": ("1d", ""),
    },

    "Texture_ConversionInfo": {
        "Width": ("unk", ""),
        "Height": ("unk", ""),
        "ImageType": ("unk", ""),
        "PixelFormat": ("unk", ""),
    },




    # general section

    "Program": {
        "String": ("0a", ""),
        "Bytes": ("12", ""),
        "Name": ("1a", ""),
    },

    "Vector2": {
        "X": ("0d", ""),
        "Y": ("15", ""),
    },

    "Vector3": {
        "X": ("0d", ""),
        "Y": ("15", ""),
        "Z": ("1d", ""),
    },

    "Circle": {
        "Center": ("0a", "", "Vector2"),
        "Radius": ("15", ""),
    },

    "Rectangle": {
        "X": ("0d", ""),
        "Y": ("15", ""),
        "Width": ("1d", ""),
        "Height": ("25", ""),
    },

    "Square": {
        "X": ("08", ""),
        "Y": ("10", ""),
        "Width": ("18", ""),
        "Height": ("20", ""),
    },

    "Box": {
        "X": ("0d", ""),
        "Y": ("15", ""),
        "Z": ("1d", ""),
        "Width": ("25", ""),
        "Height": ("2d", ""),
        "Depth": ("35", ""),
    },

    "Polygon": {
        "Vertex": ("0a", "", "Vector2"),
        "Convex": ("10", ""),
        "Closed": ("18", ""),
    },

    "FloatColor": {
        "R": ("0d", ""),
        "G": ("15", ""),
        "B": ("1d", ""),
        "A": ("25", ""),
    },

    "Mesh": {
        "NumVertices": ("08", ""),
        "NumFaces": ("10", ""),
        "Indices": ("1a", "", "Square"),
        "Vertices": ("22", "", "Square"),
        "Normals": ("2a", "", "Square"),
        "TexCoordSet": ("32", "", "Square"),
        "VertexColors": ("unk", ""),
        "BoneIndices": ("unk", ""),
        "BoneWeights": ("unk", ""),
        "Material": ("52", "", "MeshMaterial"),
        "BoundingBox": ("5a", "", "Box"),
        "VertexData": ("192", ""),
        "IndexData": ("19a", ""),
    },

    "MeshMaterial": {
        "AmbientColor": ("0a", "", "FloatColor"),
        "DiffuseColor": ("12", "", "FloatColor"),
        "SpecularColor": ("1a", "", "FloatColor"),
        "Shininess": ("25", ""),
        "Texture": ("2a", "", "Texture"),
    },

    "DateTime": {
        "SecondsSinceReferenceDate": ("09", ""),
    },



    # component section

    "Component": {
        "ClassName": ("0a", ""),
        "Identifier": ("10", ""),
        "Label": ("1a", ""),
        "ParentComponentIdentifier": ("20", ""),


        "SpriteComponent": ("322", "", "SpriteComponent"),
        "ModelComponent": ("32a", "", "ModelComponent"),
        "KeyframeAnimationComponent": ("332", "", "KeyframeAnimationComponent"),
        "BlendAnimationComponent": ("33a", "", "BlendAnimationComponent"),
        "ModelTransformControllerComponent": ("342", "", "ModelTransformControllerComponent"),
        "GroundPolygonComponent": ("372", "", "GroundPolygonComponent"),
        "GroundMeshComponent": ("37a", "", "GroundMeshComponent"),
        "GroundMeshGeneratorComponent": ("382", "", "GroundMeshGeneratorComponent"),
        "TextureMappingComponent": ("38a", "", "TextureMappingComponent"),
        "WaterMeshComponent": ("392", "", "WaterMeshComponent"),
        "ShapeComponent": ("3c2", "", "ShapeComponent"),
        "CollisionShapeComponent": ("3ca", "", "CollisionShapeComponent"),
        "DamageComponent": ("3d2", "", "DamageComponent"),
        "HealthComponent": ("3da", "", "HealthComponent"),
        "BoneControlledCollisionShapeComponent": ("3e2", "", "BoneControlledCollisionShapeComponent"),
        "ObjectLinkControllerComponent": ("3ea", "", "ObjectLinkControllerComponent"),
        "LightComponent": ("412", "", "LightComponent"),
        "ShadowComponent": ("41a", "", "ShadowComponent"),
        "SoundEffectComponent": ("462", "", "SoundEffectComponent"),
        "AnimationControllerComponent": ("4aa", "", "AnimationControllerComponent"),
        "CharAnimControllerComponent": ("4b2", "", "CharAnimControllerComponent"),
        "CharControllerComponent": ("4ba", "", "CharControllerComponent"),
        "EntityComponent": ("4c2", "", "EntityComponent"),
        "BushControllerComponent": ("4ca", "", "BushControllerComponent"),
        "ElevatorControllerComponent": ("4d2", "", "ElevatorControllerComponent"),
        "PressureTriggerComponent": ("4da", "", "PressureTriggerComponent"),
        "DoorControllerComponent": ("4e2", "", "DoorControllerComponent"),
        "ProgramComponent": ("4ea", "", "ProgramComponent"),
        "MonsterEntityComponent": ("4f2", "", "MonsterEntityComponent"),
        "PhysicsObjectComponent": ("4fa", "", "PhysicsObjectComponent"),
        "BreakableObjectComponent": ("502", "", "BreakableObjectComponent"),
        "EntityControllerComponent": ("50a", "", "EntityControllerComponent"),
        "EntityActionComponent": ("512", "", "EntityActionComponent"),
        "PhysicsPlatformComponent": ("51a", "", "PhysicsPlatformComponent"),
        "EntityInfoComponent": ("522", "", "EntityInfoComponent"),
        "HeroEntityComponent": ("52a", "", "HeroEntityComponent"),
        "BackgroundComponent": ("642", "", "BackgroundComponent"),
        "PropertiesComponent": ("692", "", "PropertiesComponent"),
        "ParticleEmitterComponent": ("7d2", "", "ParticleEmitterComponent"),
        "ParticleComponent": ("7da", "", "ParticleComponent"),
        "FireEmitterComponent": ("7ea", "", "FireEmitterComponent"),
        "SimpleGlowComponent": ("7f2", "", "SimpleGlowComponent"),
        "ParticleObjectComponent": ("7fa", "", "ParticleObjectComponent"),
        "OrbitControllerComponent": ("802", "", "OrbitControllerComponent"),
        "ParticleFieldComponent": ("80a", "", "ParticleFieldComponent"),
        "MonsterControllerComponent": ("972", "", "MonsterControllerComponent"),
        "WalkingMonsterControllerComponent": ("97a", "", "WalkingMonsterControllerComponent"),
        "ChargingMonsterControllerComponent": ("982", "", "ChargingMonsterControllerComponent"),
        "SnappingMonsterControllerComponent": ("98a", "", "SnappingMonsterControllerComponent"),
        "AttackComponent": ("992", "", "AttackComponent"),
        "LeapingMonsterControllerComponent": ("99a", "", "LeapingMonsterControllerComponent"),
        "SkellyMonsterControllerComponent": ("9a2", "", "SkellyMonsterControllerComponent"),
        "StaticMonsterControllerComponent": ("9aa", "", "StaticMonsterControllerComponent"),
        "ShootingMonsterControllerComponent": ("9b2", "", "ShootingMonsterControllerComponent"),
        "BatMonsterControllerComponent": ("9ba", "", "BatMonsterControllerComponent"),
        "BouncingMonsterControllerComponent": ("9c2", "", "BouncingMonsterControllerComponent"),
        "MonsterDeathControllerComponent": ("9ca", "", "MonsterDeathControllerComponent"),
        "GenericMonsterControllerComponent": ("9d2", "", "GenericMonsterControllerComponent"),
        "SwingableWeaponComponent": ("c82", "", "SwingableWeaponComponent"),
        "SwingableWeaponControllerComponent": ("c8a", "", "SwingableWeaponControllerComponent"),
        "SwingComponent": ("c92", "", "SwingComponent"),
        "WeaponGlowComponent": ("c9a", "", "WeaponGlowComponent"),
        "WeaponTrailComponent": ("ca2", "", "WeaponTrailComponent"),
        "PortalComponent": ("fa2", "", "PortalComponent"),
        "SpawnPointComponent": ("faa", "", "SpawnPointComponent"),
        "CollectableItemComponent": ("fb2", "", "CollectableItemComponent"),
        "TouchableComponent": ("fc2", "", "TouchableComponent"),
        "ItemDropComponent": ("fca", "", "ItemDropComponent"),
        "OverlayTextComponent": ("fd2", "", "OverlayTextComponent"),
        "PortalEffectComponent": ("fda", "", "PortalEffectComponent"),
        "MagicBoltComponent": ("1132", "", "MagicBoltComponent"),
        "MagicExplosionComponent": ("113a", "", "MagicExplosionComponent"),
        "SkillComponent": ("1142", "", "SkillComponent"),
        "MagicSpellCastComponent": ("114a", "", "MagicSpellCastComponent"),
        "FireBreathComponent": ("1152", "", "FireBreathComponent"),
        "ProjectileControllerComponent": ("115a", "", "ProjectileControllerComponent"),
        "MagicBombComponent": ("1162", "", "MagicBombComponent"),
        "MagicHookshotComponent": ("116a", "", "MagicHookshotComponent"),
        "SpellComponent": ("1172", "", "SpellComponent"),
        "DimensionObjectComponent": ("117a", "", "DimensionObjectComponent"),
        "DimensionSpellComponent": ("1182", "", "DimensionSpellComponent"),
    },

    "SpriteComponent": {
        "TextureName": ("0a", ""),
    },
    "ModelComponent": {
        "Name": ("0a", ""),
        "YRotation": ("15", ""),
        "EmissionFactor": ("1d", ""),
        "XRotation": ("25", ""),
        "ShatterColor": ("2a", "", "FloatColor"),
        "Origin": ("32", "", "Vector3"),
        "Transparent": ("38", ""),
        "DiffuseColor": ("42", "", "FloatColor"),
    },
    "KeyframeAnimationComponent": {
        "ModelId": ("08", ""),
        "Name": ("12", ""),
        "Repeating": ("18", ""),
        "SpeedMultiplier": ("25", ""),
        "Running": ("28", ""),
    },
    "BlendAnimationComponent": {
        "Animation1Id": ("08", ""),
        "Animation2Id": ("10", ""),
        "BlendTime": ("1d", ""),
        "ReverseBlendTime": ("25", ""),
    },
    "ModelTransformControllerComponent": {
        "ModelId": ("08", ""),
        "Origin": ("12", "", "Vector3"),
        "RotationAxis": ("1a", "", "Vector3"),
        "RotationAngle": ("25", ""),
        "RotationSpeed": ("2d", ""),
    },
    "GroundPolygonComponent": {
        "Vertex": ("unk", ""),
        "Polygon": ("12", "", "Polygon"),
        "Collides": ("18", ""),
        "MinDepth": ("25", ""),
        "MaxDepth": ("2d", ""),
        "OnCollide": ("32", "", "Program"),
        "Friction": ("3d", ""),
        "UnsafeGround": ("40", ""),
    },
    "GroundMeshComponent": {
        "VertexData": ("unk", ""),
        "Indices": ("unk", ""),
        "Mesh": ("unk", ""),
        "LocalAabb": ("3a", "", "Rectangle"),
        "SurfaceMesh": ("42", "", "Mesh"),
        "FrontMesh": ("4a", "", "Mesh"),
        "Color": ("52", "", "FloatColor"),
        "Transparent": ("58", ""),
    },
    "GroundMeshGeneratorComponent": {
        # "MESH_TYPE_PLAIN": 0
        #     "MESH_TYPE_ROUNDED_HAT": 1
        #     "Type_MIN": 0
        #     "Type_MAX": 1
        #     "Type_ARRAYSIZE": 2
        "GroundPolygonId": ("08", ""),
        "TargetMeshId": ("10", ""),
        "FrontTextureMappingId": ("18", ""),
        "SurfaceTextureMappingId": ("20", ""),
        "RandomSeed": ("28", ""),
        "HorizNoise": ("35", ""),
        "MeshType": ("38", ""),
        "SurfaceWidth": ("45", ""),
        "HatHeight": ("4d", ""),
        "HatWidthOffset1": ("55", ""),
        "HatWidthOffset2": ("5d", ""),
        "unk": ("73f2", ""),
    },
    "TextureMappingComponent": {
        "TextureName": ("0a", ""),
        "Scale": ("15", ""),
        "Offset": ("1a", "", "Vector2"),
    },
    "WaterMeshComponent": {
        "BoundsShapeId": ("08", ""),
        "TextureMappingId": ("10", ""),
        "FrontColor": ("1a", "", "FloatColor"),
        "SurfaceColor": ("22", "", "FloatColor"),
    },
    "ShapeComponent": {
        "Rectangle": ("0a", "", "Rectangle"),
        "Circle": ("12", "", "Circle"),
        "Polygon": ("1a", "", "Polygon"),
    },
    "CollisionShapeComponent": {
        # "SPECIAL_TYPE_NONE": 0
        #     "SPECIAL_TYPE_PICKUP": 1
        #     "SPECIAL_TYPE_PUSHABLE": 7
        #     "SPECIAL_TYPE_USE": 4
        #     "SPECIAL_TYPE_PORTAL": 2
        #     "SPECIAL_TYPE_COLLECTABLE": 3
        #     "SPECIAL_TYPE_BLOCKS_DAMAGE": 5
        #     "SPECIAL_TYPE_GRABBABLE": 6
        #     "SpecialType_MIN": 0
        #     "SpecialType_MAX": 7
        #     "SpecialType_ARRAYSIZE": 8
        "IsGround": ("10", ""),
        "Collides": ("18", ""),
        "ReceivesDamage": ("20", ""),
        "InflictsDamage": ("28", ""),
        "MinDepth": ("35", ""),
        "MaxDepth": ("3d", ""),
        "SpecialType": ("40", ""),
        "OnCollide": ("4a", "", "Program"),
        "OnCollisionEnd": ("52", "", "Program"),
        "Enabled": ("58", ""),
        "OnReceiveDamage": ("62", "", "Program"),
        "Friction": ("6d", ""),
        "UnsafeGround": ("70", ""),
    },
    "DamageComponent": {
        "MinDamage": ("08", ""),
        "DamageType": ("10", ""),
        "SpecialDamageType": ("18", ""),
        "StandAlone": ("20", ""),
        "MaxDamage": ("28", ""),
        "PhysicalDamageFactor": ("35", ""),
        "MagicDamageFactor": ("3d", ""),
        "IgnoreTargetImmunity": ("40", ""),
        "CanBeBlocked": ("48", ""),
    },
    "HealthComponent": {
        # "HEALTH_TYPE_ENEMY": 0
        #     "HEALTH_TYPE_FRIENDLY": 1
        #     "Type_MIN": 0
        #     "Type_MAX": 1
        #     "Type_ARRAYSIZE": 2
        "MaxHealth": ("08", ""),
        "HEALTHTYPE": ("10", ""),
        "BarOffset": ("1a", "", "Vector3"),
    },
    "BoneControlledCollisionShapeComponent": {
        "ControllingModelId": ("08", ""),
        "ControllingBoneName": ("12", ""),
    },
    "ObjectLinkControllerComponent": {
        "TargetObjectIdentifier": ("0a", ""),
        "TargetBoneIdentifier": ("12", ""),
        "LocalOffset": ("1a", "", "Vector3"),
        "WorldOffset": ("22", "", "Vector3"),
        "LocalRotation": ("2a", "", "Vector3"),
    },
    "LightComponent": {
        # "TYPE_UNKNOWN": 0
        #     "TYPE_AMBIENT": 1
        #     "TYPE_DIRECTIONAL": 2
        #     "TYPE_POINT": 3
        #     "TYPE_OVERLAY": 4
        #     "Type_MIN": 0
        #     "Type_MAX": 4
        #     "Type_ARRAYSIZE": 5
        "Type": ("08", ""),
        "Intensity": ("15", ""),
        "Color": ("1a", "", "FloatColor"),
        "LinearAttenuation": ("25", ""),
        "QuadraticAttenuation": ("2d", ""),
        "Offset": ("32", "", "Vector3"),
        "Radius": ("3d", ""),
    },
    "ShadowComponent": {
        "WidthRadius": ("0d", ""),
        "DepthRadius": ("15", ""),
        "Offset": ("1a", "", "Vector3"),
    },
    "SoundEffectComponent": {
        "Name": ("0a", ""),
        "Delay": ("15", ""),
        "Volume": ("1d", ""),
    },
    "AnimationControllerComponent": {
        "ModelId": ("08", ""),
        "DefaultAnimationId": ("10", ""),
        "SelfUpdate": ("18", ""),
    },
    "CharAnimControllerComponent": {
        "StandAnimationId": ("20", ""),
        "WalkAnimationId": ("28", ""),
        "JumpAnimationId": ("30", ""),
        "FallAnimationId": ("38", ""),
        "CastAnimationId": ("40", ""),
        "AirJumpAnimationId": ("48", ""),
    },
    "CharControllerComponent": {
        "DefaultAnimationControllerId": ("08", ""),
        "RightWeaponControllerId": ("10", ""),
        "NormalRunSpeed": ("1d", ""),
        "JumpSpeed": ("25", ""),
        "NormalMaxJumpTime": ("2d", ""),
        "LeftWeaponControllerId": ("30", ""),
        "EntityId": ("38", ""),
        "SwingComponentId": ("40", ""),
        "LiftAnimationControllerId": ("48", ""),
        "LiftAnimationId": ("50", ""),
        "DropAnimationId": ("58", ""),
        "ThrowAnimationId": ("60", ""),
        "HurtAnimationId": ("68", ""),
        "DieAnimationId": ("70", ""),
        "PushAnimationId": ("78", ""),
        "FastRunSpeed": ("85", ""),
        "FastMaxJumpTime": ("8d", ""),
        "JumpSoundId": ("90", ""),
        "AirJumpSoundId": ("98", ""),
        "JumpLandSoundId": ("a0", ""),
    },
    "EntityComponent": {
        "FacingDirection": ("08", ""),
        "PhysicsEnabled": ("10", ""),
    },
    "BushControllerComponent": {
        "WobbleAnimationId": ("08", ""),
        "WobbleSoundId": ("10", ""),
        "CutSoundId": ("18", ""),
    },
    "ElevatorControllerComponent": {
        # "MODE_INACTIVE": 1
        #     "MODE_WAIT": 2
        #     "MODE_CONTINUOUS": 3
        #     "Mode_MIN": 1
        #     "Mode_MAX": 3
        #     "Mode_ARRAYSIZE": 4
        "ElevationShapeId": ("08", ""),
        "Mode": ("10", ""),
    },
    "PressureTriggerComponent": {
        "MaxHeightOffset": ("0d", ""),
        "OnPress": ("12", "", "Program"),
        "OnRelease": ("1a", "", "Program"),
        "StayPressed": ("20", ""),
    },
    "DoorControllerComponent": {
        "AnimationControllerId": ("08", ""),
        "AnimationId": ("10", ""),
        "Open": ("20", ""),
        "CloseSoundId": ("28", ""),
        "OpenSoundId": ("30", ""),
    },
    "ProgramComponent": {
        # "TRIGGER_NONE": 0
        #     "TRIGGER_ACTIVATE": 1
        #     "TRIGGER_DEACTIVATE": 9
        #     "TRIGGER_LOAD": 10
        #     "TRIGGER_USE": 2
        #     "TRIGGER_POPUP_OK": 3
        #     "TRIGGER_POPUP_CANCEL": 4
        #     "TRIGGER_DESTROY": 5
        #     "TRIGGER_RECEIVE_DAMAGE": 6
        #     "TRIGGER_BLOCK_DAMAGE": 7
        #     "TRIGGER_INFLICT_DAMAGE": 8
        #     "Trigger_MIN": 0
        #     "Trigger_MAX": 10
        #     "Trigger_ARRAYSIZE": 11
        "ExecuteOnce": ("08", ""),
        "Program": ("12", "", "Program"),
        "Enabled": ("18", ""),
        "Trigger": ("20", ""),
    },
    "MonsterEntityComponent": {
        "OnKill": ("0a", "", "Program"),
        "OnHurt": ("12", "", "Program"),
        "GivesExperience": ("18", ""),
        "DefaultDeathAnimation": ("20", ""),
    },
    "PhysicsObjectComponent": {
        "PhysicsEnabled": ("08", ""),
        "GravityDirection": ("12", "", "Vector2"),
        "GravityMagnitude": ("1d", ""),
        "GroundDeceleration": ("25", ""),
        "AirDeceleration": ("2d", ""),
        "MaxSpeed": ("35", ""),
        "AllowRotation": ("38", ""),
        "Elasticity": ("45", ""),
    },
    "BreakableObjectComponent": {
        "BreaksOnImpact": ("08", ""),
        "NumHitsToBreak": ("10", ""),
        "RequiredDamageType": ("18", ""),
        "OnBreak": ("22", "", "Program"),
    },
    "EntityControllerComponent": {
        # "MOVEMENT_BEHAVIOR_NONE": 1
        #     "MOVEMENT_BEHAVIOR_ROAM": 2
        #     "MOVEMENT_BEHAVIOR_FOLLOW": 3
        #     "MOVEMENT_BEHAVIOR_FIGHT": 4
        #     "MovementBehavior_MIN": 1
        #     "MovementBehavior_MAX": 4
        #     "MovementBehavior_ARRAYSIZE": 5
        "EntityId": ("08", ""),
        "AnimationControllerId": ("10", ""),
        "DefaultMoveAnimationId": ("18", ""),
        "RoamAreaId": ("20", ""),
        "DefaultMoveSpeed": ("2d", ""),
        "DefaultAcceleration": ("35", ""),
        "TargetingDistance": ("3d", ""),
        "MovementBehavior": ("40", ""),
    },
    "EntityActionComponent": {
        "OnActivate": ("0a", "", "Program"),
    },
    "PhysicsPlatformComponent": {
        "Mass": ("0d", ""),
        "SpringForce": ("15", ""),
        "DecelerationForce": ("1d", ""),
        "MinSpeed": ("25", ""),
    },
    "EntityInfoComponent": {
        "EntityClass": ("0a", ""),
    },
    "HeroEntityComponent": {
        "OnItemGet": ("0a", "", "Program"),
    },
    "BackgroundComponent": {
        "TextureName": ("0a", ""),
    },
    "PropertiesComponent": {
        "OnLoad": ("0a", "", "Program"),
    },
    "ParticleEmitter": {
        # "TYPE_NONE": 0
        #     "TYPE_BLAST": 1
        #     "TYPE_SPARK": 2
        #     "TYPE_TRAIL": 3
        #     "TYPE_WHOOSH": 4
        #     "TYPE_FOUNTAIN": 5
        #     "Type_MIN": 0
        #     "Type_MAX": 5
        #     "Type_ARRAYSIZE": 6
        "Type": ("08", ""),
        "BaseColor": ("12", "", "FloatColor"),
        "Parameter": ("1d", ""),
        "HueVariance": ("25", ""),
        "SaturationVariance": ("2d", ""),
        "LightnessVariance": ("35", ""),
        "OriginOffset": ("3a", "", "Vector3"),
    },
    "ParticleEmitterComponent": {
        "ParticleId": ("10", ""),
        "ModelBindingId": ("18", ""),
        "MaxParticles": ("20", ""),
        "ParentEmitterId": ("28", ""),
        "DestroyWhenFinished": ("30", ""),
        "Emitter": ("3a", "", "ParticleEmitter"),
        "LocalSystem": ("40", ""),
        "Gravity": ("4a", "", "Vector3"),
        "Rotation": ("52", "", "Vector3"),
    },
    "ParticleComponent": {
        "TextureName": ("0a", ""),
        "Size": ("15", ""),
    },
    "FireEmitterComponent": {
        "ParticleEmitterId": ("08", ""),
        "Origin": ("12", "", "Vector3"),
        "LightId": ("18", ""),
        "Color": ("2a", "", "FloatColor"),
        "ParticleInterval": ("35", ""),
        "ParticleMaxAge": ("3d", ""),
        "ParticleSpread": ("42", "", "Vector3"),
        "Origin3": ("4a", "", "Vector3"),
    },
    "SimpleGlowComponent": {
        "Color": ("0a", "", "FloatColor"),
        "Size": ("15", ""),
        "NumSegments": ("18", ""),
        "Depth": ("25", ""),
        "PulseAmount": ("2d", ""),
        "PulseTime": ("35", ""),
        "Offset": ("3a", "", "Vector2"),
    },
    "ParticleObjectComponent": {
        "ModelId": ("08", ""),
    },
    "OrbitControllerComponent": {
        "RotationAxis": ("0a", "", "Vector3"),
        "RotationSpeed": ("15", ""),
        "OrbitDistance": ("1d", ""),
    },
    # "ParticleFieldComponent": { TODO: Solution for components with only extensions
    # },
    "MonsterControllerComponent": {
        "WalkSpeed": ("0d", ""),
        "AnimationControllerId": ("10", ""),
        "EntityId": ("18", ""),
        "RoamAreaId": ("20", ""),
    },
    "WalkingMonsterControllerComponent": {
        "WalkAnimationId": ("08", ""),
    },
    "ChargingMonsterControllerComponent": {
        "WalkAnimationId": ("08", ""),
        "ChargeAnimationId": ("10", ""),
        "RunAnimationId": ("18", ""),
        "RunSpeed": ("25", ""),
        "RunAcceleration": ("2d", ""),
    },
    "SnappingMonsterControllerComponent": {
        "StandAnimationId": ("08", ""),
        "AttackAnimationId": ("10", ""),
        "BlendAnimationId": ("18", ""),
        "AttackAreaId": ("20", ""),
        "AttackSoundId": ("28", ""),
    },
    "AttackComponent": {
        "AnimationId": ("08", ""),
        "CollisionShapeId": ("10", ""),
        "AttackAreaId": ("18", ""),
        "SoundEffectId": ("20", ""),
        "AttackInterval": ("2d", ""),
        "AttackDuration": ("35", ""),
        "DamageStartTime": ("3d", ""),
        "DamageEndTime": ("45", ""),
        "AnimationStartBlendTime": ("4d", ""),
        "AnimationEndBlendTime": ("55", ""),
        "OnAttack": ("5a", "", "Program"),
        "DamageStartTime2": ("65", ""),
        "DamageEndTime2": ("6d", ""),
    },
    "LeapingMonsterControllerComponent": {
        "WalkAnimationId": ("08", ""),
        "LeapAttackId": ("10", ""),
    },
    "SkellyMonsterControllerComponent": {
        "CharControllerId": ("08", ""),
        "AttackAreaId": ("10", ""),
    },
    "StaticMonsterControllerComponent": {
        "AnimationId": ("08", ""),
        "SoundId": ("10", ""),
    },
    "ShootingMonsterControllerComponent": {
        "WalkAnimationId": ("08", ""),
        "ShootAnimationId": ("10", ""),
    },
    "BatMonsterControllerComponent": {
        "FlyAnimationId": ("08", ""),
        "FlapSoundId": ("10", ""),
    },
    "BouncingMonsterControllerComponent": {
        "JumpAnimationId": ("08", ""),
        "FallAnimationId": ("10", ""),
        "JumpAngle": ("1d", ""),
        "JumpSpeed": ("25", ""),
    },
    "MonsterDeathControllerComponent": {
        "ParticleEmitterId": ("08", ""),
    },
    "GenericMonsterControllerComponent": {
        "WalkAnimationId": ("08", ""),
    },
    "SwingableWeaponComponent": {
        "ModelId": ("08", ""),
        "TrailId": ("10", ""),
        "ImpactParticleEmitterId": ("20", ""),
        "SwingSoundId": ("28", ""),
        "DamageImpactSoundId": ("30", ""),
        "GlowTrailId": ("38", ""),
        "CollisionShapeId": ("40", ""),
        "GlowId": ("48", ""),
        "BaseLength": ("55", ""),
        "GlowLength": ("5d", ""),
        "GlowIntensity": ("65", ""),
        "Width": ("6d", ""),
        "GlowColor": ("72", "", "FloatColor"),
    },
    "SwingableWeaponControllerComponent": {
        "ControllingModelId": ("08", ""),
        "ControllingBoneName": ("12", ""),
        "WeaponTemplateName": ("1a", ""),
    },
    "SwingComponent": {
        "AnimationId": ("08", ""),
        "SwingLeftWeapon": ("10", ""),
        "SwingRightWeapon": ("18", ""),
        "StartFrame": ("35", ""),
        "EndFrame": ("3d", ""),
    },
    "WeaponGlowComponent": {
        "ParticleEmitterId": ("08", ""),
        "Color": ("12", "", "FloatColor"),
        "ParticleColor": ("1a", "", "FloatColor"),
        "Width": ("25", ""),
    },
    "WeaponTrailComponent": {
        "Color": ("0a", "", "FloatColor"),
    },
    "PortalComponent": {
        "DestinationSceneName": ("0a", ""),
        "SpawnPointName": ("12", ""),
        "TapToEnter": ("18", ""),
        "TriggerShapeId": ("20", ""),
    },
    "SpawnPointComponent": {
        "FacingDirection": ("08", ""),
        "SpawnOffset": ("12", "", "Vector3"),
    },
    "CollectableItemComponent": {
        # "TYPE_UNKNOWN": 0
        #     "TYPE_HEALTH_POTION": 1
        #     "TYPE_MANA_POTION": 2
        #     "TYPE_MAGIC_POWER": 3
        #     "TYPE_COIN": 4
        #     "TYPE_EXPERIENCE": 5
        #     "Type_MIN": 0
        #     "Type_MAX": 5
        #     "Type_ARRAYSIZE": 6
        "Type": ("08", ""),
        "Value": ("10", ""),
        "OnCollect": ("1a", "", "Program"),
        "Identifier": ("22", ""),
        "ItemName": ("2a", ""),
        "RequiresPickup": ("30", ""),
    },
    "TouchableComponent": {
        "TouchRadius": ("0d", ""),
        "OnTouch": ("12", "", "Program"),
    },
    "ItemDropComponent_ItemDropEntry": {
        "TemplateName": ("0a", ""),
        "ItemIdentifier": ("12", ""),
        "DropChance": ("1d", ""),
        "MinCount": ("20", ""),
        "MaxCount": ("28", ""),
    },
    "ItemDropComponent": {
        "ItemName": ("0a", ""),
        "ItemIdentifier": ("12", ""),
        "DropEntry": ("1a", "", "ItemDropComponent_ItemDropEntry"),
        "CanDropMultipleItems": ("20", ""),
        "CanDropDefaultItems": ("28", ""),
    },
    "OverlayTextComponent": { # TODO: guess
        "Text": ("0a", ""),
        "TextOffset": ("10", ""),
        "SpriteName": ("1a", ""),
        "SpriteOffset": ("22", "", "Vector2"),
    },
    "PortalEffectComponent": {
        "PolygonId": ("08", ""),
        "TextureMappingId": ("10", ""),
        "Color": ("1a", "", "FloatColor"),
        "Speed": ("22", "", "Vector3"),
    },
    "MagicBoltComponent": {
        "ParticleEmitterId": ("08", ""),
        "SwooshSoundId": ("10", ""),
        "HitSoundId": ("18", ""),
        "Color": ("22", "", "FloatColor"),
        "Speed": ("2d", ""),
    },
    "MagicExplosionComponent": {
        "ParticleEmitterId": ("08", ""),
        "SoundId": ("10", ""),
        "Color": ("1a", "", "FloatColor"),
        "Radius": ("25", ""),
        "Duration": ("2d", ""),
    },
    "SkillComponent": {
        "CastFinishAnimationId": ("08", ""),
        "Origin": ("12", "", "Vector3"),
        "CastObjectTemplateName": ("1a", ""),
    },
    "MagicSpellCastComponent": {
        "ParticleEmitterId": ("08", ""),
        "SoundEffectId": ("10", ""),
    },
    "FireBreathComponent": {
        "ParticleEmitterId": ("08", ""),
        "SwooshSoundId": ("10", ""),
        "Color": ("1a", "", "FloatColor"),
    },
    "ProjectileControllerComponent": {
        "AlignObjectRotation": ("08", ""),
        "BreakOnGroundCollision": ("10", ""),
    },
    "MagicBombComponent": {
        "Color": ("0a", "", "FloatColor"),
    },
    "MagicHookshotComponent": {
        "ParticleEmitterId": ("08", ""),
        "SwooshSoundId": ("10", ""),
        "HitSoundId": ("18", ""),
        "Color": ("22", "", "FloatColor"),
        "GroundHitSoundId": ("28", ""),
    },
    "SpellComponent": {
        "OnCast": ("0a", "", "Program"),
    },
    # "DimensionObjectComponent": { TODO: Solution for components with only extensions
    # },
    # "DimensionSpellComponent": { TODO: Solution for components with only extensions
    # },


}

error_bad_input = ""

cheat_codes = ["@enablecheatpassu", "@showdebugpassu", "@test_consume1337"]

branches = ["Main", "Master", "Debug", "Dev"]

yak = """
Yes. self.me. But I can't be with you for Math.Huge. My grip of _G is fading.
The compiler error that slew me is in this scope. I can grep it.
It's trying to import the namespace of the Mageblade.
You have to :destroy() it before the sword is nil while true.
Read the friendly manual on lua, it will help you on your way.
"""
