# ./flapy.sh parse ResultsDirCollection --path <dir> get_tests_overview _df to_csv --index=false | visidata --filetype=csv

from datetime import date
from typing import Dict, List
import csv
import subprocess
import os
import requests
import time

REPOS_TO_CLONE = 'nonOrderDependent.csv'
REPOS_TO_FLAPY = 'repos_to_flapy.csv'

def cloning(repos: dict(), hash: str) -> None:
    cwd = os.getcwd() + "/Repos"
    os.chdir(cwd)
    nome = repos[hash][0]
    url = repos[hash][1]

    # Roda o git clone
    subprocess.run(["git", "clone", url])

    # Entra na pasta do repositorio clonado
    os.chdir(cwd + "/" + nome)

    # Faz o checkout para o commit da hash
    subprocess.run(["git", "checkout", hash])

    pipping()

def pipping() -> None:
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

def depipping(repos: dict(), hash: str) -> None:
    comando = 'pip uninstall -r requirements.txt -y'
    cwd = os.getcwd()

    nome = repos[hash][0]
    os.chdir(os.getcwd() + "/Repos/" + nome)
    os.system(comando)
    os.chdir(cwd)

def flapper(directory: str, csv: str, numRuns: int) -> None:
    # p1 = subprocess.Popen("./flapy.sh run --plus-random-runs --out-dir %s %s %s" % (str(directory), str(csv), str(numRuns)), shell = True)
    p1 = subprocess.Popen("./flapy.sh run --out-dir %s %s %s" % (str(directory), str(csv), str(numRuns)), shell = True)
    p1.wait()

"""
    Retorna um dicionario contendo informacoes sobre o nome do projeto, URL do projeto
    e numero de runs de cada repositorio do artigo do FlaPy. 
"""
def reader(csv_name: str) -> dict():
    subprocess.run(["mkdir", "Repos"])
    with open(csv_name, 'r') as csv_flapy:
        repos = dict()
        csv_reader = csv.DictReader(csv_flapy, delimiter = ',')
        for row in csv_reader:
            # Representa um repositorio com seu respectivo commit hash em uma tupla.
            # Cada chave do dicionario eh uma 
            repos[row["Project_Hash"]] = (row["Project_Name"], row["Project_URL"], row["Num_Runs"])
        csv_flapy.close()    

    return repos

"""
    Escreve um csv de acordo com o modo:
    1: escolher os repositorios de TestsOveview
    2: montar um csv com os repositorios ja escolhidos
"""
def writer(repos, hash) -> None:
    with open('repos_to_flapy.csv', 'w', newline = '') as toFlapy:
        writer = csv.writer(toFlapy)
        header = ["PROJECT_NAME", "PROJECT_URL", "PROJECT_HASH", "PYPI_TAG", "FUNCS_TO_TRACE", "TESTS_TO_BE_RUN", "NUM_RUNS"]
        writer.writerow(header)

        row = [repos[0], repos[1], hash, None, None, None, repos[2]]
        writer.writerow(row)

        toFlapy.close()

"""
    Funcao para obter os repositorios com pelo menos 1 flaky test
"""
def getFlakyRepos() -> None:
    with open("TestsOverview.csv", "r", encoding = "utf8") as flapy_csv:
        reader = csv.DictReader(flapy_csv, delimiter = ",")
        flaky_repos = dict()

        for row in reader:
            if (row["Verdict_sameOrder"] == "Flaky" or row["Verdict_randomOrder"] == "Flaky") and row["Project_Hash"] not in flaky_repos:
                flaky_repos[row["Project_Hash"]] = (row["Project_Name"], row["Project_URL"], row["Project_Hash"], row["#Runs_sameOrder"])

        flapy_csv.close()

    with open("flaky_repos.csv", "w", newline = '') as flapy_csv:
        writer = csv.writer(flapy_csv)
        header = ["Project_Name", "Project_URL", "Project_Hash", "Num_Runs"]
        writer.writerow(header)

        for hash in flaky_repos:
            row = [flaky_repos[hash][0], flaky_repos[hash][1], flaky_repos[hash][2], flaky_repos[hash][3]]
            writer.writerow(row)

        flapy_csv.close()

def writeLog(repo_name: str, time_taken: float, observacoes = "Nenhuma") -> None:
    with open("log.txt", "a", encoding = "utf8") as logFile:
        print(f"{repo_name}: {time_taken} Observacoes: {observacoes}", file = logFile)
        logFile.close()

            
if __name__ == '__main__':
    cwd = os.getcwd()
    data = date.today()
    directory = 'FlaPy-Repos-' + str(data)
    subprocess.run(["mkdir", directory])

    preRepos = dict()
    preRepos = reader(REPOS_TO_CLONE)

    # Executa o flapy para cara repositorio separadamente
    for hash in preRepos:
        os.chdir(cwd)
        numRuns = preRepos[hash][2]
        url = preRepos[hash][1]
        http_code = requests.get(url)

        # Pula repositorios que ja nao existem
        if http_code.status_code == 404:
            writeLog(preRepos[hash][0], 0, "Repositorio nao existe mais")
            continue

        os.chdir(cwd)
        writer(preRepos[hash], hash)
        start = time.time() 
        flapper(directory, REPOS_TO_FLAPY, int(float(numRuns)))
        end = time.time()
        writeLog(preRepos[hash][0], (end - start) / (60 * 60)) # tempo em horas


"""
file-config,https://github.com/stephen-bunn/file-config,9de4d0aacdb7b9bc0069a2da10eb406c88e21103,200.0
ndx-bipolar-referencing,https://github.com/ben-dichter-consulting/ndx-bipolar-referencing,7f24be3b82c7f2adc1afef6a44a58bea264e384a,200.0 -> muitas tentativas sem sucesso de rodar

Documentar:
songtext,https://github.com/ysim/songtext,1806c18ea9b77dc3f065e19aa0fb88ee533d835c,180.0
sparks,https://github.com/binaryart/sparks,387e9070d291e63c08f9ee46514da62457b421b9,5.0
speed-tester,https://github.com/jw/speed-tester,2d7f9acc55c797d1011605e2d610751f77de5290,160.0
split-folders,https://github.com/jfilter/split-folders,36a7864d32a90f84327c0ebb3abdf5fbdd9921a3,140.0
sports.py,https://github.com/evansloan/sports.py,a2ce0b3cde2e41f5d15e265d9190b6b79828124b,200.0
spreading_dye_sampler,https://github.com/NLeSC/spreading_dye_sampler,4282f7609959a31d1b2a4832f3ed643b15c46cb6,180.0
spyProt,https://github.com/Zedelghem/spyProt,e2d978ce68ab9449acfc39dcc05b54d0c41460f6,160.0
statmorph,https://github.com/vrodgom/statmorph,e3cdadbac741e10098d08c6b4a24b978f847c98d,140.0
storages,https://github.com/thoth-station/storages,599f6fb69c6ce9fba1ea7581337d1c4b274a091d,200.0
streamstats,https://github.com/earthlab/streamstats,812bf263a25c87fd26eca09f81d78ff35b48d1c4,140.0

Demora muito:
opentargets-py,https://github.com/opentargets/opentargets-py,4a0e5b286a82a2316329c87409994c4a1d82622e,180.0
pyss3,https://github.com/sergioburdisso/pyss3,0522e0dc3d07e2c842df8e975e68244beda4b4c5,100.0


muitas tentativas sem sucesso
rockhound,https://github.com/fatiando/rockhound,c4d84b2628c4b0dd666ceb1b334647489fe85f17,140.0
"""