#
#   Copyright(c) 2013-2016, Wind River Systems, Inc. 
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     * Neither the name of Wind River Systems nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#   OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <misc.h>

void printstruct(struct online_cpus *cpuarray)
{
    int i;
    printf("num cpus: %d\n", cpuarray->numcpus);
    for (i=0;i<cpuarray->numcpus;i++)
        printf("%d: %d\n", i, cpuarray->status[i]);
}


struct online_cpus cpus = {15, {1,0,0,0,0,0,1,1,1,0,0,0,1,1,1}};
int main()
{
    char *str, *str2;
    struct online_cpus *newcpus;
    printf("initial: \n");
    printstruct(&cpus);
    printf("string:\n");
    str = "0,6-8,12-14";
    newcpus = range_to_array(str);
    printf("fromstring: \n");
    printstruct(newcpus);
    newcpus = range_to_array("");
    printf("empty: \n");
    printstruct(newcpus);
    newcpus = range_to_array("0--2");
    newcpus = range_to_array("0-1-2");
    newcpus = range_to_array("0,,2");
    newcpus = range_to_array("0,-2");
    newcpus = range_to_array("1,2-a");

    return 0;
}
