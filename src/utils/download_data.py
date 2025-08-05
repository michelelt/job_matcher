import kagglehub
import shutil
import pathlib as pl
import os


# Download latest version
path = kagglehub.dataset_download("promptcloud/indeed-job-posting-dataset")
path = pl.Path(path)
path = path.joinpath('home', 'sdf', 'marketing_sample_for_trulia_com-real_estate__20190901_20191031__30k_data.csv')

src = path
dst = './data/job_posts'
shutil.move(src, dst)
print("Path to dataset files:", path)




path = kagglehub.dataset_download("youssefkhalil/resumes-images-datasets")
dst = './data'
shutil.move(path, dst)

print("Path to dataset files:", path)


