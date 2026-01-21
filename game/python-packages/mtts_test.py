import mtts

with open("token.txt", "r") as f:
    token = f.read().strip()
mtts_instance = mtts.MTTS(token=token, cache_path="E:\GithubKu\MAICA_MTTSubmod\game\Submods\MAICA_MTTSubmod\cache")
#print("Token verify:", mtts_instance._verify_token())
res = mtts_instance.generate("boring!!")
mtts_instance.save_audio(res.data, "test2.wav")