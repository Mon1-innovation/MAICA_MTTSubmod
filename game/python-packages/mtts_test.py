import MTTS

with open("token.txt", "r") as f:
    token = f.read().strip()
mtts = MTTS.MTTS(token=token, cache_path="E:\GithubKu\MAICA_MTTSubmod\game\Submods\MAICA_MTTSubmod\cache")
#print("Token verify:", mtts._verify_token())
res = mtts.generate("boring!!")
mtts.save_audio(res.data, "test2.wav")