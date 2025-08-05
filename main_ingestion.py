from src.insertion.insert_job_post import insert_job_posts_to_chromadb
from src.insertion.insert_resume import process_resumes_to_chroma, get_file_extensions
from pathlib import Path


def main():
    csv_file = "/Users/mc/Desktop/resume_matcher/data/job_posts/marketing_sample_for_trulia_com-real_estate__20190901_20191031__30k_data.csv"
    insert_job_posts_to_chromadb(csv_file, collection_name='job_posts',overwrite=True)

    root_directory = Path("./data/Resumes Datasets")
    
    extensions_found = get_file_extensions(root_directory)
    print("Found extensions:", extensions_found)

    process_resumes_to_chroma(
        root_dir=root_directory,
        collection_name="resumes",
        overwrite=True
    )