"""Explicit local C test harness. Compiles/runs your source, not a sandbox."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

HARNESS = r'''
#include <assert.h>
#include <stddef.h>
#include <stdio.h>
int parse(const unsigned char *, size_t, const unsigned char **, size_t *);
int main(void) {
    const unsigned char good[]={0,3,65,0,66}, empty[]={0,0}, max[]={0,8,1,2,3,4,5,6,7,8};
    const unsigned char short_header[]={0}, truncated[]={0,4,65}, trailing[]={0,1,65,66};
    const unsigned char excess[]={0,9,1,2,3,4,5,6,7,8,9};
    const unsigned char *payload=NULL; size_t n=99;
    assert(parse(good,sizeof good,&payload,&n) && n==3 && payload[1]==0 && payload[2]==66);
    assert(parse(empty,sizeof empty,&payload,&n) && n==0);
    assert(parse(max,sizeof max,&payload,&n) && n==8);
    assert(!parse(NULL,0,&payload,&n));
    assert(!parse(good,sizeof good,NULL,&n));
    assert(!parse(good,sizeof good,&payload,NULL));
    assert(!parse(short_header,sizeof short_header,&payload,&n));
    assert(!parse(truncated,sizeof truncated,&payload,&n));
    assert(!parse(trailing,sizeof trailing,&payload,&n));
    assert(!parse(excess,sizeof excess,&payload,&n));
    puts("C CONTRACT PASS: also inspect ownership and your own additional cases.");
    return 0;
}
'''
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',default='project-parser-starter.c')
parser.add_argument('--sanitize',action='store_true')
args=parser.parse_args()
source=Path(args.source).resolve(strict=True)
with tempfile.TemporaryDirectory(prefix='bifrost-c-project-') as folder:
    root=Path(folder)
    (root/'main.c').write_text(HARNESS,encoding='utf-8')
    command=['gcc','-std=c11','-Wall','-Wextra','-Werror']
    if args.sanitize: command+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
    command += [str(source),str(root/'main.c'),'-o',str(root/'test')]
    subprocess.run(command,check=True,timeout=30)
    subprocess.run([str(root/'test')],check=True,timeout=10,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=1'})
