### aws-s3-oss.md

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
	end_point := "http://192.168.163.121:9000" //endpoint设置，不要动


	sess, err := session.NewSession(&aws.Config{
		Credentials:      credentials.NewStaticCredentials(access_key, secret_key, ""),
		Endpoint:         aws.String(end_point),
		Region:           aws.String("us-east-1"),
		DisableSSL:       aws.Bool(true),
		S3ForcePathStyle: aws.Bool(false), //virtual-host style方式，不要修改
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


	// bucket后跟，go run ....go bucketname
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