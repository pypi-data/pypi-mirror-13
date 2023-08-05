from pytcga.tcga_requests import tcga_request

def request_rnaseq_data(disease_code,
                        with_clinical=True,
                        wait_time=30,
                        cache=True,):

    data_path = tcga_request(disease=disease_code,
                               level='3',
                               center='7',
                               platformType='RNASeqV2',
                               platform='IlluminaHiSeq_RNASeqV2',
                               wait_time=30)data_p
    print(os.listdir(data_path))