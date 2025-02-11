package kics

import (
	"context"
	"fmt"
	"reflect"
	"testing"

	"github.com/Checkmarx/kics/internal/storage"
	"github.com/Checkmarx/kics/internal/tracker"
	"github.com/Checkmarx/kics/pkg/engine"
	"github.com/Checkmarx/kics/pkg/engine/provider"
	"github.com/Checkmarx/kics/pkg/model"
	"github.com/Checkmarx/kics/pkg/parser"
	dockerParser "github.com/Checkmarx/kics/pkg/parser/docker"
	jsonParser "github.com/Checkmarx/kics/pkg/parser/json"
	terraformParser "github.com/Checkmarx/kics/pkg/parser/terraform"
	yamlParser "github.com/Checkmarx/kics/pkg/parser/yaml"
	"github.com/Checkmarx/kics/pkg/resolver"
	"github.com/Checkmarx/kics/pkg/resolver/helm"
)

// TestService tests the functions [GetVulnerabilities(), GetScanSummary(),StartScan()] and all the methods called by them
func TestService(t *testing.T) {
	mockParser, mockFilesSource, mockResolver := createParserSourceProvider("../../test/fixtures/test_helm")

	type fields struct {
		SourceProvider provider.SourceProvider
		Storage        Storage
		Parser         *parser.Parser
		Inspector      *engine.Inspector
		Tracker        Tracker
		Resolver       *resolver.Resolver
	}
	type args struct {
		ctx     context.Context
		scanID  string
		scanIDs []string
	}
	type want struct {
		vulnerabilities []model.Vulnerability
		severitySummary []model.SeveritySummary
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		want    want
		wantErr bool
	}{
		{
			name: "service",
			fields: fields{
				Inspector:      &engine.Inspector{},
				Parser:         mockParser,
				Tracker:        &tracker.CITracker{},
				Storage:        storage.NewMemoryStorage(),
				SourceProvider: mockFilesSource,
				Resolver:       mockResolver,
			},
			args: args{
				ctx:     nil,
				scanID:  "scanID",
				scanIDs: []string{"scanID"},
			},
			wantErr: false,
			want: want{
				vulnerabilities: []model.Vulnerability{},
				severitySummary: nil,
			},
		},
	}
	for _, tt := range tests {
		s := &Service{
			SourceProvider: tt.fields.SourceProvider,
			Storage:        tt.fields.Storage,
			Parser:         tt.fields.Parser,
			Inspector:      tt.fields.Inspector,
			Tracker:        tt.fields.Tracker,
			Resolver:       tt.fields.Resolver,
		}
		t.Run(fmt.Sprintf(tt.name+"_get_vulnerabilities"), func(t *testing.T) {
			got, err := s.GetVulnerabilities(tt.args.ctx, tt.args.scanID)
			if (err != nil) != tt.wantErr {
				t.Errorf("Service.GetVulnerabilities() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want.vulnerabilities) {
				t.Errorf("Service.GetVulnerabilities() = %v, want %v", got, tt.want)
			}
		})
		t.Run(fmt.Sprintf(tt.name+"_get_scan_summary"), func(t *testing.T) {
			got, err := s.GetScanSummary(tt.args.ctx, tt.args.scanIDs)
			if (err != nil) != tt.wantErr {
				t.Errorf("Service.GetScanSummary() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want.severitySummary) {
				t.Errorf("Service.GetScanSummary() = %v, want %v", got, tt.want)
			}
		})
		t.Run(fmt.Sprintf(tt.name+"_start_scan"), func(t *testing.T) {
			if err := s.StartScan(tt.args.ctx, tt.args.scanID, true); (err != nil) != tt.wantErr {
				t.Errorf("Service.StartScan() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func createParserSourceProvider(path string) (*parser.Parser,
	*provider.FileSystemSourceProvider, *resolver.Resolver) {
	mockParser, _ := parser.NewBuilder().
		Add(&jsonParser.Parser{}).
		Add(&yamlParser.Parser{}).
		Add(terraformParser.NewDefault()).
		Add(&dockerParser.Parser{}).
		Build([]string{""})

	mockFilesSource, _ := provider.NewFileSystemSourceProvider([]string{path}, []string{})

	mockResolver, _ := resolver.NewBuilder().Add(&helm.Resolver{}).Build()

	return mockParser, mockFilesSource, mockResolver
}
