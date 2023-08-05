#!/usr/bin/python3
#
# This file is part of sarracenia.
# The sarracenia suite is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2008-2015
#
# Questions or bugs report: dps-client@ec.gc.ca
# sarracenia repository: git://git.code.sf.net/p/metpx/git
# Documentation: http://metpx.sourceforge.net/#SarraDocumentation
#
# sr_sender.py : python3 program consumes product messages and send them to another pump
#                and announce the newly arrived product on that pump. If the post_broker
#                is not given... it is accepted, the products are sent without notices.
#
#
# Code contributed by:
#  Michel Grenier - Shared Services Canada
#  Last Changed   : Jan  5 08:31:59 EST 2016
#
########################################################################
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, 
#  but WITHOUT ANY WARRANTY; without even the implied warranty of 
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
#============================================================
# usage example
#
# sr_sender [options] [config] [start|stop|restart|reload|status]
#
# sr_sender connects to a broker. For each product it has selected, it sends it onto the other
# broker and reannounce it there.
#
# conditions:
#
# broker                  = where sarra is running (manager)
# exchange                = xpublic
# message.headers[to_clusters] verified if destination includes remote pump ?
#
# do_send                 = a script supporting the protocol defined in the destination
# destination             = an url of the credentials of the remote server and its options (see credentials)
# directory               = the placement is mirrored usually
# accept/reject           = pattern matching what we want to poll in that directory
#
# (optional... only if message are posted after products are sent)
# post_broker             = remote broker (remote manager)
# post_exchange           = xpublic
# document_root           = if provided, extracted from the url if present
# url                     = build from the destination/directory/product
# product                 = the product placement is mirrored by default
#                           unless if accept/reject are under a directory option
# post_message            = incoming message with url changes
#                           message.headers['source']  left as is
#                           message.headers['cluster'] left as is 
#                           option url : gives new url announcement for this product
#============================================================

#

import os,sys,time

try :    
         from sr_amqp           import *
         from sr_consumer       import *
         from sr_ftp            import *
         from sr_instances      import *
         from sr_message        import *
         from sr_poster         import *
except : 
         from sarra.sr_amqp      import *
         from sarra.sr_consumer  import *
         from sarra.sr_ftp       import *
         from sarra.sr_instances import *
         from sarra.sr_message   import *
         from sarra.sr_poster    import *

class sr_sender(sr_instances):

    def __init__(self,config=None,args=None):
        sr_instances.__init__(self,config,args)
        self.defaults()
        self.configure()

    def check(self):
        self.connected     = False 

        # to clusters requiered

        if self.post_broker != None and self.to_clusters == None :
           self.logger.error("Need to know post_broker cluster name")
           self.logger.error("-to option is mandatory in this case\n")
           sys.exit(1)

        # fallback bindings to "all"

        if self.exchange  == None :
           self.exchange   = 'xpublic'

        if self.bindings == []  :
           key = self.topic_prefix + '.#'
           self.bindings.append( (self.exchange,key) )
           self.logger.debug("*** BINDINGS %s"% self.bindings)

        # no queue name allowed... force this one

        self.queue_name  = 'q_' + self.broker.username + '.'
        self.queue_name += self.program_name + '.' + self.config_name 

        # check destination

        self.details = None
        if self.destination != None :
           ok, self.details = self.credentials.get(self.destination)

        if self.destination == None or self.details == None :
           self.logger.error("destination option incorrect or missing\n")
           sys.exit(1)

        # check destination
        if self.post_broker != None and self.post_exchange == None :
           self.post_exchange = self.exchange

    def close(self):
        self.consumer.close()
        if self.post_broker : self.poster.close()
        self.connected = False 

    def configure(self):

        # a destination must be provided

        self.destination  = None
        self.post_broker  = None
        self.currentDir   = None

        # consumer defaults

        if hasattr(self,'manager'):
           self.broker = self.manager
        self.exchange  = 'xpublic'

        # most of the time we want to mirror product directory and share queue

        self.mirror      = True
        self.queue_share = True

        # Should there be accept/reject option used unmatch are accepted

        self.accept_unmatch = True

        # load/reload all config settings

        self.general()
        self.args   (self.user_args)
        self.config (self.user_config)

        # verify / complete settings

        self.check()

        self.setlog()

    def connect(self):

        # =============
        # create message
        # =============

        self.msg = sr_message(self.logger)

        # =============
        # consumer
        # =============

        self.consumer          = sr_consumer(self)
        self.msg.log_publisher = self.consumer.publish_back()
        self.msg.log_exchange  = self.log_exchange

        # =============
        # poster
        # =============

        if self.post_broker :
           self.poster           = sr_poster(self)

           self.msg.publisher    = self.poster.publisher
           self.msg.pub_exchange = self.post_exchange

        self.connected        = True 

    # =============
    # __do_send__
    # =============

    def __do_send__(self):

        self.logger.info("sending/copying %s " % self.msg.local_file)

        try :
                if   self.do_send :
                     return self.do_send(self)

                elif self.msg.url.scheme in ['ftp','ftps']  :
                     return ftp_send(self)

                elif self.msg.url.scheme == 'sftp' :
                     try    : from sr_sftp       import sftp_download
                     except : from sarra.sr_sftp import sftp_download
                     return sftp_send(self)

        except :
                (stype, svalue, tb) = sys.exc_info()
                self.logger.error("Sender  Type: %s, Value: %s,  ..." % (stype, svalue))
                self.msg.log_publish(503,"Unable to process")
                self.logger.error("Could not send")

        self.msg.log_publish(503,"Service unavailable %s" % self.msg.url.scheme)

    def help(self):
        print("Usage: %s [OPTIONS] configfile [start|stop|restart|reload|status]\n" % self.program_name )
        print("OPTIONS:")
        print("instances <nb_of_instances>      default 1")
        print("\nAMQP consumer broker settings:")
        print("\tbroker amqp{s}://<user>:<pw>@<brokerhost>[:port]/<vhost>")
        print("\t\t(MANDATORY)")
        print("\nAMQP Queue bindings:")
        print("\texchange             <name>          (default: xpublic)")
        print("\ttopic_prefix         <amqp pattern>  (default: v02.post)")
        print("\tsubtopic             <amqp pattern>  (default: #)")
        print("\t\t  <amqp pattern> = <directory>.<directory>.<directory>...")
        print("\t\t\t* single directory wildcard (matches one directory)")
        print("\t\t\t# wildcard (matches rest)")
        print("\nAMQP Queue settings:")
        print("\tdurable              <boolean>       (default: False)")
        print("\texpire               <minutes>       (default: None)")
        print("\tmessage-ttl          <minutes>       (default: None)")
        print("\nFile settings:")
        print("\tdocument_root        <document_root> (MANDATORY)")
        print("\taccept    <regexp pattern>           (default: None)")
        print("\tmirror               <boolean>       (default True)")
        print("\treject    <regexp pattern>           (default: None)")
        print("\tstrip      <strip count (directory)> (default 0)")
        print("\nDestination/message settings:")
        print("\tdo_send              <script>        (default None)")
        print("\tdestination          <url>           (MANDATORY)")
        print("\tpost_document_root   <document_root> (default None)")
        print("\turl                  <url>           (MANDATORY)")
        print("\ton_message           <script>        (default None)")
        print("\tto                   <cluster>       (MANDATORY)")
        print("\nAMQP posting broker settings (optional):")
        print("\tpost_broker amqp{s}://<user>:<pw>@<brokerhost>[:port]/<vhost>")
        print("\t\t(default: manager amqp broker in default.conf)")
        print("\tpost_exchange        <name>          (default xs_postusername)")
        print("\ton_post              <script>        (default None)")
        print("DEBUG:")
        print("-debug")

    # =============
    # __on_message__
    # =============

    def __on_message__(self):

        # only if sending to another pump
        if self.post_broker != None :
           # the message has not specified a destination.
           if not 'to_clusters' in self.msg.headers :
              self.msg.log_publish(403,"Forbidden : message without destination amqp header['to_clusters']")
              self.logger.error("message without destination amqp header['to_clusters']")
              return False

           # this instances of sr_sender runs,
           # to send product to cluster: self.to_clusters.
           # since self.to_clusters might be a list, we check for 
           # and try matching any of this list to the message's to_clusters list

           ok = False
           for cluster in self.msg.to_clusters.split(',') :
              if cluster.strip() != self.to_clusters :  continue
              ok = True
              break

           if not ok :
              self.logger.warning("skipped : not for remote cluster...")
              return False

        if self.destination[:3] == 'ftp' :
            # 'i' cannot be supported by ftp/ftps
            # we cannot offset in the remote file to inject data
            #
            # FIXME instead of dropping the message
            # the inplace part could be delivered as 
            # a separate partfile and message set to 'p'
            if  self.msg.partflg == 'i':
                logger.error("ftp, inplace part file not supported")
                msg.log_publish(499,'ftp delivery problem')
                return False

        # invoke user defined on_message when provided

        if self.on_message : return self.on_message(self)

        return True

    # =============
    # process message  
    # =============

    def process_message(self):

        self.logger.info("Received %s '%s' %s" % (self.msg.topic,self.msg.notice,self.msg.hdrstr))

        #=================================
        # setting up message with sr_sender config options
        # self.set_local  : setting local info for the file/part
        # self.set_remote : setting remote server info for the file/part
        #=================================

        self.set_local()
        self.set_remote()

        #=================================
        # now message is complete : invoke __on_message__
        #=================================

        ok = self.__on_message__()
        if not ok : return ok

        #=================================
        # proceed to send :  has to work
        #=================================

        while True : 
              ok = self.__do_send__()
              if ok : break

        #=================================
        # publish our sending
        #=================================

        self.msg.set_topic_url('v02.post',self.remote_url)
        self.msg.set_notice(self.remote_url,self.msg.time)
        self.__on_post__()
        self.msg.log_publish(201,'Published')

        return True

    def run(self):

        # configure

        self.configure()

        # present basic config

        self.logger.info("sr_sender run")

        # loop/process messages

        self.connect()

        while True :
              try  :
                      #  consume message
                      ok, self.msg = self.consumer.consume()
                      if not ok : continue

                      #  process message (ok or not... go to the next)
                      ok = self.process_message()

              except:
                      (stype, svalue, tb) = sys.exc_info()
                      self.logger.error("Type: %s, Value: %s,  ..." % (stype, svalue))


    def set_local(self):

        self.local_root  = ''
        self.local_rpath = ''

        path  = '%s' % self.msg.path
        token = path.split('/')

        if self.document_root != None : self.local_root  = self.document_root
        if len(token) > 1             : self.local_rpath = '/'.join(token[:-1])
        self.filename = token[-1]


        # Local directory (directory created if needed)

        self.local_dir    = self.local_root + '/' + self.local_rpath
        self.local_dir    = self.local_dir.replace('//','/')
        self.local_file   = self.filename

        self.local_path   = self.local_dir   + '/' + self.filename

        self.local_offset = self.msg.offset
        self.local_length = self.msg.lenght


    def set_remote(self):

        self.remote_root  = ''
        if self.post_document_root != None : self.remote_root = self.post_document_root

        # mirror case by default
        self.remote_rpath = self.local_rpath

        # a target directory was provided
        if self.currentDir != None:
           self.remote_rpath = self.currentDir

        # no mirror and no directory ...
        if not self.mirror and self.currentDir == None :
           self.logger.warning("no mirroring and directory unset : assumed None ")
           self.remote_rpath = ''

        # default to localfilename

        self.remote_file = self.local_file

        self.remote_dir  = self.remote_root + '/' + self.remote_rpath
        self.remote_path = self.remote_dir  + '/' + self.remote_file

        self.remote_urlstr = self.destination + self.remote_path + '/' + self.remote_file
        self.remote_url    = urllib.parse.urlparse(self.remote_urlstr)

    # =============
    # __on_post__ posting of message
    # =============

    def __on_post__(self):

        # should always be ok

        ok = self.msg.publish( )

        # invoke on_post when provided anyway

        if ok and self.on_post : ok = self.on_post(self)

        return ok

    def reload(self):
        self.logger.info("%s reload" % self.program_name)
        self.close()
        self.run()

    def start(self):
        self.logger.info("%s start" % self.program_name)
        self.run()

    def stop(self):
        self.logger.info("%s stop" % self.program_name)
        self.close()
        os._exit(0)

# ===================================
# MAIN
# ===================================

def main():

    action = None
    args   = None
    config = None

    if len(sys.argv) >= 3 :
       action = sys.argv[-1]
       config = sys.argv[-2]
       if len(sys.argv) > 3: args = sys.argv[1:-2]

    sender = sr_sender(config,args)

    if   action == 'reload' : sender.reload_parent()
    elif action == 'restart': sender.restart_parent()
    elif action == 'start'  : sender.start_parent()
    elif action == 'stop'   : sender.stop_parent()
    elif action == 'status' : sender.status_parent()
    else :
           sender.logger.error("action unknown %s" % action)
           sys.exit(1)

    sys.exit(0)



# =========================================
# direct invocation
# =========================================

if __name__=="__main__":
   main()
