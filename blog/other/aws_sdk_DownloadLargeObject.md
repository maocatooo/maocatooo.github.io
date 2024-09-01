---
title: AWS S3 下载文件翻倍占用内存
date: 2024-06-25 18:00:00
tags: [aws,s3]
---

在aws doc (https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/example_s3_Scenario_UsingLargeFiles_section.html)上面找的下载大文件示例,直接粘贴运行,没问题,提交上线

源代码
```go
// DownloadLargeObject uses a download manager to download an object from a bucket.
// The download manager gets the data in parts and writes them to a buffer until all of
// the data has been downloaded.
func (basics BucketBasics) DownloadLargeObject(bucketName string, objectKey string) ([]byte, error) {
	var partMiBs int64 = 10
    downloader := manager.NewDownloader(basics.S3Client, func(d *manager.Downloader) {
		d.PartSize = partMiBs * 1024 * 1024
	})
	buffer := manager.NewWriteAtBuffer([]byte{})
	_, err := downloader.Download(context.TODO(), buffer, &s3.GetObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(objectKey),
	})
	if err != nil {
		log.Printf("Couldn't download large object from %v:%v. Here's why: %v\n",
			bucketName, objectKey, err)
	}
	return buffer.Bytes(), err
}
```

后面客户反馈业务上传500M的文件,接口报错了,查了一下就是服务重启了,本地复现了一下发现下载这个500M的文件,使用的内存却到了2G+,直接内存爆掉,服务重启

排查了一下发现就是manager.NewWriteAtBuffer这个结构内存,在使用判断切片容量不足的情况下,直接重新新建了一个新的切片,旧的切片没有及时清理

```go
//https://github.com/aws/aws-sdk-go-v2/blob/4ed838eab2a963cb16301501c8b8c3e29dac4c20/feature/s3/manager/types.go#L162
func (b *WriteAtBuffer) WriteAt(p []byte, pos int64) (n int, err error) {
	pLen := len(p)
	expLen := pos + int64(pLen)
	b.m.Lock()
	defer b.m.Unlock()
	if int64(len(b.buf)) < expLen {
		if int64(cap(b.buf)) < expLen {
			if b.GrowthCoeff < 1 {
				b.GrowthCoeff = 1
			}
			newBuf := make([]byte, expLen, int64(b.GrowthCoeff*float64(expLen)))
			copy(newBuf, b.buf)
			b.buf = newBuf
		}
		b.buf = b.buf[:expLen]
	}
	copy(b.buf[pos:], p)
	return pLen, nil
}
```

解决办法:

```go
buffer := manager.NewWriteAtBuffer([]byte{})
```

获取S3文件的size
初始化切片, 直接给到文件对应的大小

```go
headInput := &s3.HeadObjectInput{
	Bucket: bucketName,
	Key:    objectKey,
}

headObject, err := s3c.client.HeadObject(context.TODO(), headInput)
if err != nil {
	return nil, err
}
buf := make([]byte, ptr.ToInt64(headObject.ContentLength))
buffer := manager.NewWriteAtBuffer(buf)
```
