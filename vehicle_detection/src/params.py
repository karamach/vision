global_params = {
    # Color FE
    'src_space': 'RGB',
    'dst_space': 'HSV',
    'spatial_size': (16, 16),
    'bins': 32,
    'range': (0, 256),

    # Hog FE
    'orientation': 9,
    'pixels_per_cell': 8,
    'cells_per_block': 2,
    'channel': 'ALL',
    'color_feature': True,
    'hog_feature': True,
    'feature_vector': False,
    'visualise': False,

    # Data
    # 'train_pos': '../train_images/vehicles_smallset/cars1,'
    #              '../train_images/vehicles_smallset/cars2,'
    #              '../train_images/vehicles_smallset/cars3',
    # 'train_neg': '../train_images/non-vehicles_smallset/notcars1,'
    #              '../train_images/non-vehicles_smallset/notcars2,'
    #              '../train_images/non-vehicles_smallset/notcars3',

    'train_pos': '../train_images/vehicles/GTI_Far,../train_images/vehicles/GTI_Left,'
                 '../train_images/vehicles/GTI_MiddleClose,../train_images/vehicles/GTI_Right,'
                 '../train_images/vehicles/KITTI_extracted',
    'train_neg': '../train_images/non-vehicles/Extras,../train_images/non-vehicles/GTI',

    # Sliding window params
    'x_start_stop': [None, None],
    'y_start_stop': [350, 700],
    'xy_overlap': (0.5, 0.5),
    'window_beg_size': 96,
    'window_end_size': 200,
    'window_incr_size': 40,
    # 'out_mode': 'candidate',
    # 'out_mode': 'label',
    # 'out_mode': 'heat_map',
    'out_mode': 'heat_map,label,candidate',

    # Label tracker
    'num_frames': 20,
    'threshold': .6,
    'num_cont_frames': 4,

    # Pipeline test
    # 'test_data_in': '../test_images/',
    # 'test_data_out': '../test_images_out/',
    # 'test_data_in': '../project_video_frames/',
    # 'test_data_out': '../project_video_frames_out/'
    'test_data_in': '../project_video_frames_small/',
    'test_data_out': '../project_video_frames_small_out/'
}
