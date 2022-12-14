# AUTOGENERATED! DO NOT EDIT! File to edit: ../01_dataset.ipynb.

# %% auto 0
__all__ = ['ds_exists', 'mk_dataset', 'get_dataset', 'push_dataset', 'get_pip_library', 'get_pip_libraries', 'get_local_ds_ver',
           'create_dependency_dataset', 'push_fastai_learner']

# %% ../01_dataset.ipynb 4
import json, os, subprocess, shutil
from pathlib import Path
from .setup import *

# %% ../01_dataset.ipynb 7
def ds_exists(dataset_slug, # Dataset slug (ie "zillow/zecon")
                   path='.' # path to fastkaggle.json file or None
             ):
    '''Check if a dataset exists'''
    md_path = Path(Path(path)/'dataset-metadata.json')
    assert not md_path.exists(),'dataset-metadata.json already exists. Use a path that is not a kaggle dataset'
    try: 
        api=import_kaggle()
        api.dataset_metadata(dataset_slug,path)
        md_path.unlink()
        return True
    except Exception as ex:
        if '404' in str(ex): return False
        else: raise ex  

# %% ../01_dataset.ipynb 9
def mk_dataset(dataset_path, # Local path to create dataset in
               title, # Name of the dataset
               force=False, # Should it overwrite or error if exists?
               upload=True, # Should it upload and create on kaggle
               cfg_path='.', # path to fastkaggle.json file or None
               **kwargs # Config dict to overwrite or replace fastkaggle.json
              ):
    '''Creates minimal dataset metadata needed to push new dataset to kaggle'''
    cfg = get_config_values(cfg_path,**kwargs)
    dataset_path = Path(dataset_path)
    dataset_path.mkdir(exist_ok=force,parents=True)
    api = import_kaggle()
    api.dataset_initialize(dataset_path)
    md = json.load(open(dataset_path/'dataset-metadata.json'))
    md['title'] = title
    md['id'] = md['id'].replace('INSERT_SLUG_HERE',title)
    json.dump(md,open(dataset_path/'dataset-metadata.json','w'))
    if upload: (dataset_path/'empty.txt').touch()
    api.dataset_create_new(str(dataset_path),public=True,dir_mode='zip',quiet=True)

# %% ../01_dataset.ipynb 11
def get_dataset(dataset_slug, # Dataset slug (ie "zillow/zecon")
                dataset_path, # Local path to download dataset to
                unzip=True, # Should it unzip after downloading?
                force=False # Should it overwrite or error if dataset_path exists?
               ):
    '''Downloads an existing dataset and metadata from kaggle'''
    if not force: assert not Path(dataset_path).exists()
    api = import_kaggle()
    api.dataset_metadata(dataset_slug,str(dataset_path))
    api.dataset_download_files(dataset_slug,str(dataset_path))
    if unzip:
        zipped_file = Path(dataset_path)/f"{dataset_slug.split('/')[-1]}.zip"
        import zipfile
        with zipfile.ZipFile(zipped_file, 'r') as zip_ref:
            zip_ref.extractall(Path(dataset_path))
        zipped_file.unlink()

# %% ../01_dataset.ipynb 13
def push_dataset(dataset_path, # Local path where dataset is stored 
                 version_comment, # Comment associated with this dataset update
                quiet=True
                ):
    '''Push dataset update to kaggle.  Dataset path must contain dataset metadata file'''
    api = import_kaggle()
    api.dataset_create_version(str(dataset_path),version_comment,dir_mode='zip',quiet=quiet)

# %% ../01_dataset.ipynb 15
def get_pip_library(pip_library, # name of library for pip to install
                    cfg_path='.', # path to fastkaggle.json file or None
                     **kwargs # Config dict to overwrite or replace fastkaggle.json
                   ):    
    '''Download the whl files for pip_library and store in dataset_path'''
    cfg = get_config_values(cfg_path,**kwargs)['DEFAULT']
    
    pip_cmd=cfg['pip_cmd']
    dataset_path = Path(cfg_path)/cfg['data_path']/pip_library

    bashCommand = f"{pip_cmd} download {pip_library} -d {dataset_path}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return process,output,error

# %% ../01_dataset.ipynb 17
def get_pip_libraries(directory_name,
                     cfg_path='.', # path to fastkaggle.json file or None
                     **kwargs # Config dict to overwrite or replace fastkaggle.json
                   ):    
    cfg = get_config_values(cfg_path,**kwargs)['DEFAULT']
    
    pip_cmd=cfg['pip_cmd']
    dataset_path = Path(cfg_path)/cfg['data_path']/directory_name
    libraries = cfg['required_libraries']

    bashCommand = f"{pip_cmd} download {libraries} -d {dataset_path}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return process,output,error

# %% ../01_dataset.ipynb 19
def get_local_ds_ver(lib_path, # Local path dataset is stored in
                     lib # Name of library (ie "fastcore")
                    ):
    '''checks a local copy of kaggle dataset for library version number'''
    wheel_lib_name = lib.replace('-','_')
    local_path = (lib_path/f"library-{lib}")
    lib_whl = local_path.ls().filter(lambda x: wheel_lib_name in x.name.lower())
    if 1==len(lib_whl):
        return re.search(f"(?<={wheel_lib_name}-)[\d+.]+\d",lib_whl[0].name.lower())[0]
    elif 0<len(local_path.ls().filter(lambda x: 'dist' in x.name)):
        lib_whl = (local_path/'dist').ls().filter(lambda x: wheel_lib_name in x.name.lower())
        if 1==len(lib_whl):
            return re.search(f"(?<={wheel_lib_name}-)[\d+.]+\d",lib_whl[0].name.lower())[0]
    return None

# %% ../01_dataset.ipynb 20
def create_dependency_dataset(version_notes = "New Update",
                              cfg_path='.', # path to fastkaggle.json file or None
                              **kwargs # Config dict to overwrite or replace fastkaggle.json
                           ):        
    retain = ["dataset-metadata.json"]
    cfg = get_config_values(cfg_path,**kwargs)['DEFAULT']
    
    pip_cmd=cfg['pip_cmd']
    local_path = Path(cfg_path)/cfg['data_path']/cfg['libraries_dataset_name']
    ds_slug = f"{cfg['datasets_username']}/{cfg['libraries_dataset_name']}"
    
    print(f"-----Downloading or Creating Dataset if needed")
    if local_path.exists(): pass
    elif ds_exists(ds_slug): get_dataset(ds_slug,str(local_path))
    else:                    mk_dataset(local_path,cfg['libraries_dataset_name'])
    
    print(f"-----Checking dataset files against pip")
    orig_ds = Path(local_path).ls().sorted()
    for item in local_path.ls():
        if item.name in retain: pass
        elif item.is_dir(): shutil.rmtree(item)
        else: item.unlink()      
    get_pip_libraries(cfg['libraries_dataset_name'],cfg_path,**kwargs) 
    new_ds = Path(local_path).ls().sorted()
    
    if orig_ds != new_ds: 
        print(f"-----Updating {cfg['libraries_dataset_name']} in Kaggle")
        push_dataset(local_path,version_notes)
    else: print(f"-----Kaggle dataset already up to date")
    print(f"{ds_slug} update complete")

# %% ../01_dataset.ipynb 23
def push_fastai_learner(learner, # Fastai Learner
                        model_fname, # ie `model1.pkl`
                        version_comment, # dataset versioning
                        cfg_path='.', # path to fastkaggle.json file or None
                        **kwargs # Config dict to overwrite or replace fastkaggle.json
                           ):        
    '''Exports a learner and updates kaggle dataset'''
    cfg = get_config_values(cfg_path,**kwargs)['DEFAULT']
    
    local_path = Path(cfg_path)/cfg['data_path']/cfg['model_dataset_name']
    ds_slug = f"{cfg['datasets_username']}/{cfg['model_dataset_name']}"
    
    print(f"-----Downloading or Creating Dataset if needed")
    if local_path.exists(): pass
    elif ds_exists(ds_slug): get_dataset(ds_slug,str(local_path))
    else:                    mk_dataset(local_path,cfg['model_dataset_name'])
    
    print(local_path)
    orig_path = learner.path
    learner.path = local_path
    learner.export(model_fname)
    learner.path = orig_path
    push_dataset(local_path,version_comment)
    print(f"{ds_slug} update complete")
