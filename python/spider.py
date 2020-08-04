#!/bin/python3

# This spider lists out links to all the pages of a given website
# It also lists out the links to other websites and the number of times
# those links are mentioned ( they are called  connections here )
# visited means that the site data corresponding to the url has been parsed

import sys # for exit and accepting command line arguments
import requests as r

class spider:
    # Internal links are  links that point to a page in the same site
    # External links are links that point to content in a different site
    def __init__(self,verbose,connection_,index_link):
        self.internal_links=[] # stores all the internal links found
        self.tmp_internal_links=[] # stores internal links found for a particular link
        self.external_links=[] # stores all external links
        self.connections={} # stores addresses of sites that are frequently reffered to and the number of times its reffered to
        self.tmp_external_links=[] # stores internal links found for a particular link
        self.visited_links=[] # stores all links that are already visited
        self.verbose=verbose # flag which decides the verbosity
        self.connection_=connection_ # flag which decides if processing links for connections is required
        self.index_link=index_link # url supplied by the user
        self.index={} # dictionary that stores all the visited links and the internal and external links found corresponding to a particular link


# check if a link is eligible to be added to the internal_links list
# criteria for eligibility:
# 1. the link should not be visited
# 2. the link should point to a page within the site

    def add_internal_link(self,tmp_buffer):
        if len(tmp_buffer)>0 and tmp_buffer not in self.internal_links and tmp_buffer not in self.visited_links and tmp_buffer not in self.tmp_internal_links:
            self.tmp_internal_links.append(tmp_buffer)        

# sends a req to the corresponding link and if an error occurs reports it
            
    def req(self,link):
        try:
            req=r.get(link).text.splitlines()
        except Exception as exp:
            print("Request Error : ",exp)
            sys.exit(0)
        return req

# prints the link being requested and clear the temporary lists
    
    def parser_init(self,link):
        if self.verbose:
            print("{} : {}".format(len(self.visited_links)+1,link),end="")
        else:
            print(link)
        self.tmp_internal_links.clear()
        self.tmp_external_links.clear()

# processess a line in the raw response to the request and extracts the links
        
    def buffer_processing(self,buff):
        tmp_buffer=i.split('href=')[1]
        if tmp_buffer[0] is '"':
            tmp_buffer=tmp_buffer.split('"')[1].split('"')[0]
        elif tmp_buffer[0] is "'":
            tmp_buffer=tmp_buffer.split("'")[1].split("'")[0]
        return tmp_buffer

# function that handels the parsing of responses
    
    def parser(self,link):
        req=self.req(link) # sends a request to the given link
        self.visited_links.append(link) # adds the requested link to visited list
        for i in req:
            if 'href' in i:
                try:
                    tmp_buffer=self.buffer_processing(i)
                    if len(tmp_buffer)>1 and tmp_buffer[0] is '/':
                        self.add_internal_link(tmp_buffer)
                    elif len(tmp_buffer)>1 and ("https://" in tmp_buffer or "http://" in tmp_buffer):
                        # the following if statement checks if the site has
                        # links starting with http or https but points content
                        # on the site
                        if self.index_link.split('/')[-1] in tmp_buffer:
                            link=tmp_buffer.split(self.index_link)[1]
                            self.add_internal_link(link)
                        else:
                            self.tmp_external_links.append(tmp_buffer)
                except:
                    pass;
        # updates the main lists that store the links
        self.internal_links=self.internal_links+self.tmp_internal_links
        self.external_links=self.external_links+self.tmp_external_links
        if self.verbose:
            print("\nLinks Remaining: {}\n".format(len(self.internal_links)))

# creates a dictionary with internal and external keys and adds it to
# the index dictionary.
            
    def make_dict(self,tmp_internal_links,tmp_external_links,key_name):
        internal_dictionary={}
        internal_dictionary.update(Internal_Link=tmp_internal_links.copy(),External_Links=tmp_external_links.copy())
        self.index[key_name]=internal_dictionary

# processess the external_links list to find connections
# to other sites and counts the number of times those links
# were reffered
        
    def connection(self):
        print("\nProcessing External Links...\n")
        for link in self.external_links:
            if "https://" in link:
                link=link.split("https://")[1].split('/')[0]
            elif "http://" in link:
                link=link.split("http://")[1].split('/')[0]
            if link not in self.connections.keys():
                self.connections[link]=1
            else:
                self.connections[link]=self.connections[link]+1

# displays the summary and the connection details
                
    def display(self):
        print("\n----------Summary----------\n")
        print("Total Links Processed :",len(self.visited_links))
        print("External Links Caught :",len(self.external_links))
        if self.connection_:
            print("\n----------Connections----------\n")
            for key,value in self.connections.items():
                print("{} : {}".format(key,value))

# controls the flow of the program
                
    def handler(self):
        if self.index_link[-1] is '/': # check if the given link has a / in the end and removes it in the next statement
            self.index_link=self.index_link[:-1]
        self.parser(self.index_link)
        self.make_dict(self.tmp_internal_links,self.tmp_external_links,self.index_link)
        # the first link in the internal_links list is always requested
        # and the link is removed from the list
        while len(self.internal_links):
            link=self.index_link+self.internal_links[0] # because internal lists are stored without "http(s)" and the name of the site
            self.parser(link)
            self.make_dict(self.tmp_internal_links,self.tmp_external_links,link)
            self.visited_links.append(self.internal_links[0])
            self.internal_links.pop(0)
        if self.connection_:
            self.connection()
        self.display()


def help():
    print("spider.py [OPTIONS] <URL>\nOptions:\n\t-v\tVerbose\n\t-c\tExternal Connections")

def exit_():
    help()
    sys.exit(0)
    
if __name__=="__main__":
    args={'v':0,'c':0} # used to set the verbosity and connection flags
    if len(sys.argv)==1: # minimum of two arguments required where the first is always the file name
        print("\nMissing arguments !\n")
        exit_()
    for i in sys.argv:
        # checks for parameters
        if len(i)==2 and i[0] is '-' and i[1] in args.keys():
            args[i[1]]=1
        elif i[0] is 'h' and ("https://" in i or "http://" in i):
            link=i
        elif i is sys.argv[0]:
            pass
        else:
            print("\nInvalid arguments !\n")
            exit_()
    if link:
        s=spider(args['v'],args['c'],link);
        s.handler()
    else:
        print("\nInvalid URL or URL not specified !\n")
        exit_()
#EOF
