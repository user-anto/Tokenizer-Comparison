.PHONY: fetch, tokenize, clean, table, commit

fetch:
	uv run python src/tokcomp/get_lemmy.py --limit $(l) --min_words $(w)

tokenize:
	uv run python src/tokcomp/compare_tokenizer.py

table:
	uv run python src/tokcomp/make_table.py

clean:
	uv run python src/tokcomp/clean.py

pipeline:
	$(MAKE) fetch l=$(l) w=$(w)
	$(MAKE) tokenize
	$(MAKE) clean
	$(MAKE) table

commit:
	git add .
	git commit -m $(m)
	git push -u origin main