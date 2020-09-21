def apply_asm_publish_data(asm_node, file_location):
    """
    Reads in the data found in the assembly XML file and applies that to the assembly
    cache.  This is expected to be used in a shot context, i.e. in a lighting file.

    :param asm_node: The name of a top level assembly node, i.e. 'testAssembly_asm_ref'.
    :type: str

    :param file_location: The location on disk to write out the assembly to.
    :type: str

    :return: The success of the operation.
    :type: bool
    """
    # Make sure the file exists on disk.
    if not file_location:
        IO.error('There is no assembly location data published for this shot.')
        return None
    # check to see if the assembly exists in the file
    asm_namespace = asm_node.split('_asm_ref')[0]
    if not cmds.namespace(exists=':test_assembly'):
        IO.error('There are no namespaces in the file that match the assembly.')

    sel = cmds.listRelatives(':' + asm_namespace + ':' + 'master', type='transform')
    if not sel:
        IO.error('There is no assembly cache in the scene.')
        return None
    # Read in the XML file and store it in a dictionary.
    reader = XMLReader(file_location)
    # dictionary of objects inside the assembly
    dict = reader.read_xml()
    # one step lower
    asm_dict =dict.values()[0]
    object_keys = dict.values()[0].keys()
    for o_key in object_keys:
        transform_dict = asm_dict[o_key]
        transform_keys = transform_dict.keys()
        for t_key in transform_keys:
            transform_values = transform_dict[t_key]
            transform_values = transform_values[1:len(transform_values)-1]
            tranform_list = transform_values.split(',')
            x = float(tranform_list[0])
            y = float(tranform_list[1])
            z = float(tranform_list[2])

            # parse name select the object
            split_list = o_key.split(":")
            object =split_list[len(split_list)-1]
            object_name =asm_namespace + ':' + object

            cmds.select(object_name)

            # apply transform to assembly objects
            if t_key == 'rotation':
                cmds.xform( absolute = True, rotation = (x, y, z))
            elif t_key == 'translation':
                cmds.xform(absolute=True, translation=(x, y, z))
            elif t_key == 'scale':
                cmds.xform(absolute=True, scale =(x, y, z))

def publish_asm_location_data(asm_node, file_location):
    """
    Writes out the location data for all of the geometry in an assembly.  This is
    expected to be used in a shot context, i.e. from animation.

    :param asm_node: The name of a top level assembly node, i.e. 'testAssembly_asm_ref'.
    :type: str

    :param file_location: The location on disk to write out the assembly to.
    :type: str

    :return: The success of the operation.
    :type: bool
    """
    # Make sure it exists.
    if not cmds.objExists(asm_node):
        IO.warning("The assembly node provided, '%s', does not seem to exist." % asm_node)
        return None

    # # Switch all the assembly parts to be scene representation.
    # result = toggle_asm_rep([asm_node], 'scene')
    # if not result:
    #     return None

    # Find all the translation nodes under the root node.
    results = cmds.listRelatives(asm_node, allDescendents=True, type='transform',
                                 fullPath=True)
    keep    = []
    for result in results:
        if result.endswith(GroupNames.PROXY):
            continue
        if result.endswith(COMMON_LABELS.PROXY):
            continue
        keep.append(result)

    # Write out the location of each, recording translation, rotation, and scale.
    xml_dict = AutoVivification()
    for transform in keep:
        obj_trans = cmds.xform(transform, translation=True, query=True)
        obj_rot   = cmds.xform(transform, rotation=True, query=True)
        obj_scale = cmds.xform(transform, scale=True, relative=True, query=True)
        xml_dict[asm_node][transform]['translation'] = str(obj_trans)
        xml_dict[asm_node][transform]['rotation']    = str(obj_rot)
        xml_dict[asm_node][transform]['scale']       = str(obj_scale)
    writer = XMLWriter(file_location, xml_dict)
    writer.write_xml()
