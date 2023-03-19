### <center> Gorm 中使用 Postgres 的 json </center>

官方json文档 https://www.postgresql.org/docs/12/functions-json.html

```go
package main

import (
	"database/sql/driver"
	"encoding/json"
	"fmt"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var db *gorm.DB

func initPgsql() {
	dsn := "host=192.168.163.121 user=postgres password=postgres dbname=test port=5432 sslmode=disable TimeZone=Asia/Shanghai"
	var err error
	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		panic(err)
	}
}

// User 用户
type User struct {
	gorm.Model
	Name    string
	Profile Profile `gorm:"type:json" json:"profile"`
}

// Profile 个人信息
type Profile struct {
	Email   string `json:"email"`
	PhoneNo string `json:"phoneNo"`
}

// Value 实现方法
func (p Profile) Value() (driver.Value, error) {
	return json.Marshal(p)
}

// Scan 实现方法
func (p *Profile) Scan(input interface{}) error {
	return json.Unmarshal(input.([]byte), p)
}

func main() {
	initPgsql()
	err := db.AutoMigrate(&User{})
	if err != nil {
		panic(err)
	}
	u := User{
		Name: "maocat",
		Profile: Profile{
			Email:   "maocatooo@gmail.com",
			PhoneNo: "18888888888",
		},
	}
	db.Save(&u)

	u.Profile.PhoneNo = "13666666666"
	db.Save(&u)

	var u1 User

	db.Debug().
		Where(gorm.Expr("profile->>'email' = ?", "maocatooo@gmail.com")).
		First(&u1)
	fmt.Println(u1.Name)
	fmt.Println(u1.Profile)
}

```