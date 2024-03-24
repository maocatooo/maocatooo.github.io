---
title: 使用 AWS-SDK 上传文件到 MinIO
date: 2022-03-06
tags: [MinIO, Golang]
---

[//]: # (### <center>使用 AWS-SDK 上传文件到 MinIO</center>)

公司内网环境自建的 MinIO 作为对象存储,而外网的对象存储则是使用的阿里云服务

`MinIO`和`阿里云` 都兼容亚马逊(AWS) 的S3协议, 为此使用 AWS-SDK 上传服务生成的数据内容

docker 创建一个 MinIO 的容器

MINIO_ROOT_USER 和 MINIO_ROOT_PASSWORD 就是 9001 端口的登录的账号密码, 也是AK和SK(也可以进入后台自己更换)

```
docker run -p 9000:9000 -p 9001:9001 --name minio1 -v ~/minio/data:/data -e "MINIO_ROOT_USER=AKIAIOSFODNN7EXAMPLE" -e "MINIO_ROOT_PASSWORD=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" quay.io/minio/minio server /data --console-address ":9001"

```

```
go get github.com/aws/aws-sdk-go@v1.44.70
```


```golang
package main

import (
	"bytes"
	"fmt"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	_ "github.com/aws/aws-sdk-go/service/s3/s3manager"
	"os"
)

func NewSess() *session.Session {
	access_key := "AKIAIOSFODNN7EXAMPLE"
	secret_key := "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
	end_point := "http://192.168.163.121:9000" //endpoint设置, 不要动


	sess, err := session.NewSession(&aws.Config{
        // credentials.NewStaticCredentials 这里第三个参数是token, 在使用 aliyun-sdk 时会获取的对应的值 
		Credentials:      credentials.NewStaticCredentials(access_key, secret_key, ""),
		Endpoint:         aws.String(end_point),
		Region:           aws.String("us-east-1"),
		DisableSSL:       aws.Bool(true),

		/*
		// false 会使用 virtual-host style方式,  http://192.168.163.121:9000 -> http://bucket.192.168.163.121:9000
		// true 会使用 强制使用路径方式,  http://192.168.163.121:9000 -> http://192.168.163.121:9000/bucket
		*/
		S3ForcePathStyle: aws.Bool(true),
	})

	if err != nil {
		panic(err)
	}
	return sess
}

func main() {


	get_bucket(NewSess())
	get_file_and_folder(NewSess(), "test")
	getFile(NewSess(), "test", "新建 文本文档.txt")
	uploadFile(NewSess(), "test", "新建 文本文档1.txt", "im data in 新建 文本文档1.txt")
}

func exitErrorf(msg string, args ...interface{}) {
	fmt.Fprintf(os.Stderr, msg+"", args...)
	os.Exit(1)
}

func get_bucket(sess *session.Session) {

	svc := s3.New(sess)
	result, err := svc.ListBuckets(nil)
	if err != nil {
		exitErrorf("Unable to list buckets, %v", err)
	}

	fmt.Println("Buckets:")

	for _, b := range result.Buckets {
		fmt.Printf("* %s created on %s",
			aws.StringValue(b.Name), aws.TimeValue(b.CreationDate))
	}

	for _, b := range result.Buckets {
		fmt.Printf("\n%s", aws.StringValue(b.Name))
	}

}

func get_file_and_folder(sess *session.Session, bucket string) {


	// bucket后跟, go run ....go bucketname
	fmt.Println()
	fmt.Println(bucket)

	svc := s3.New(sess)

	params := &s3.ListObjectsInput{
		Bucket:             aws.String(fmt.Sprint("/", bucket)),
		Prefix:             aws.String(""),
	}
	resp, err := svc.ListObjects(params)

	if err != nil {
		exitErrorf("Unable to list items in bucket %q, %v", bucket, err)
	}

	for _, item := range resp.Contents {
		fmt.Println("Name:         ", *item.Key)
		fmt.Println("Last modified:", *item.LastModified)
		fmt.Println("Size:         ", *item.Size)
		fmt.Println("Storage class:", *item.StorageClass)
		fmt.Println("")
	}

}

func getFile(sess *session.Session, bucket, item string) {


	file, err := os.Create(item)
	if err != nil {
		exitErrorf("Unable to open file %q, %v", err)
	}

	defer file.Close()

	downloader := s3manager.NewDownloader(sess)

	numBytes, err := downloader.Download(file,
		&s3.GetObjectInput{
			Bucket: aws.String(fmt.Sprint("/", bucket)),
			Key:    aws.String(item),
		})
	if err != nil {
		exitErrorf("Unable to download item %q, %v", item, err)
	}

	fmt.Println("Downloaded", file.Name(), numBytes, "bytes")
}

func uploadFile(sess *session.Session, bucket string, filename, fileData string) {

	uploader := s3manager.NewUploader(sess)

	_, err := uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(fmt.Sprint("/", bucket)),
		Key: aws.String(filename),
		Body: bytes.NewReader([]byte(fileData)),
	})
	if err != nil {
		// Print the error and exit.
		exitErrorf("Unable to upload %q to %q, %v", filename, bucket, err)
	}

	fmt.Printf("Successfully uploaded %q to %q ", filename, bucket)
}
```