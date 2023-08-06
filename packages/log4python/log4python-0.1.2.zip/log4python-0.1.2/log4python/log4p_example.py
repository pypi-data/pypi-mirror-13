'''log4j2.xml
<?xml version="1.0" encoding="UTF-8"?>
<Configuration monitorInterval="60">
    <Appenders>
        <File name="A1" fileName="A1.log" append="false">
            <PatternLayout pattern="%d %-5p [%t] %C{2} (%F:%L) - %m%n"/>
        </File>
        <Console name="STDOUT" target="SYSTEM_OUT">
            <PatternLayout pattern="%d %-5p [%t] %C{2} (%F:%L) - %m%n"/>
        </Console>
    </Appenders>
    <Loggers>
        <Logger name="data" level="error" additivity="false">
            <AppenderRef ref="A1"/>
        </Logger>
        <Root level="debug">
            <AppenderRef ref="A1"/>
        </Root>
    </Loggers>
</Configuration>
'''

config ={
    'monitorInterval' : 10,
    'loggers' :{
        'xxx' :{
            'level': "INFO",
            'additivity' : False,
            'AppenderRef' : ['A1']
            },
        'root' :{
            'level' : "ERROR",
            'AppenderRef' : ['error_root']
        }
    },

    'appenders' :{
        'A1' :{
            'type' :"file",
            'FileName' :"A2.log",
            'PatternLayout' :"[%(levelname)s-%(lineno)d] %(asctime)s %(message)s"
        },
        'error_root' :{
            'type' :"file",
            'FileName' :"error_root.log",
            'PatternLayout' :"[%(levelname)s-%(lineno)d] %(asctime)s %(message)s"
        },
        'console' :{
            'type' :"console",
            'target' :"console",
            'PatternLayout' :"[%(levelname)s] %(asctime)s %(message)s"
        }
    }
}
