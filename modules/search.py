import webbrowser as wb
import wikipedia

class SearchModule:
    def search(self,query):
        wb.get().open_new('https://www.google.com/search?q='+query)

    def watch(self,query):
        wb.get().open_new('https://www.youtube.com/results?search_query='+query)

    def getWiki(self,query):
        try:
            results = wikipedia.summary(query, sentences=2)
            return results
        except:
            return "Could not find query"