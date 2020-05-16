# base image
FROM node:alpine

# set working directory

RUN mkdir -p /usr/src/
WORKDIR /usr/src/

# install and cache app dependencies

RUN apk add --no-cache git
RUN apk add --no-cache openssh
RUN git clone https://github.com/hadas-schlessinger/front_end.git
WORKDIR /usr/src/front_end


RUN npm install

# start app
CMD ["npm", "start"]